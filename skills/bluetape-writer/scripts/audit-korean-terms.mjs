#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_RULES = path.resolve(SCRIPT_DIR, "../references/terminology-rules.json");

/**
 * Replace code spans with spaces while preserving line and column positions.
 * Reader-facing prose remains available to the checks; identifiers do not
 * produce false positives.
 */
export function maskTechnicalTokens(text) {
  return text
    .replace(/```[\s\S]*?```/g, (match) => match.replace(/[^\n]/g, " "))
    .replace(/`[^`\n]+`/g, (match) => match.replace(/[^\n]/g, " "));
}

export function loadRules(rulesPath = DEFAULT_RULES) {
  return JSON.parse(fs.readFileSync(rulesPath, "utf8"));
}

function lineAndColumn(text, offset) {
  const before = text.slice(0, offset);
  const lines = before.split("\n");
  return { line: lines.length, column: lines.at(-1).length + 1 };
}

function compileCheck(check) {
  const flags = check.flags ?? "gu";
  return new RegExp(check.pattern, flags.includes("g") ? flags : `${flags}g`);
}

export function rulesForSeries(rules, series) {
  const selected = rules.series?.[series];
  if (!selected) {
    throw new Error(`Unknown terminology rule series: ${series}`);
  }
  return selected;
}

export function auditText(text, { file = "<memory>", series = "clinic-appointment", rules } = {}) {
  const ruleSet = rulesForSeries(rules ?? loadRules(), series);
  const prose = maskTechnicalTokens(text);
  const findings = [];

  for (const check of ruleSet.checks ?? []) {
    const expression = compileCheck(check);
    for (const match of prose.matchAll(expression)) {
      const value = match[0];
      const offset = match.index ?? 0;
      const position = lineAndColumn(text, offset);
      findings.push({
        file,
        line: position.line,
        column: position.column,
        ruleId: check.id,
        severity: check.severity ?? "error",
        match: value,
        message: check.message,
        replacement: check.replacement ?? null,
      });
    }
  }

  return findings.sort((left, right) =>
    left.file.localeCompare(right.file) ||
    left.line - right.line ||
    left.column - right.column ||
    left.ruleId.localeCompare(right.ruleId),
  );
}

function parseArgs(argv) {
  const options = { format: "text", rulesPath: DEFAULT_RULES, series: "clinic-appointment", paths: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") {
      options.help = true;
    } else if (argument === "--json") {
      options.format = "json";
    } else if (argument === "--rules") {
      options.rulesPath = path.resolve(argv[++index]);
    } else if (argument === "--series") {
      options.series = argv[++index];
    } else if (argument.startsWith("-")) {
      throw new Error(`Unknown option: ${argument}`);
    } else {
      options.paths.push(path.resolve(argument));
    }
  }
  return options;
}

function collectFiles(entries) {
  const files = [];
  const visit = (entry) => {
    const stat = fs.statSync(entry);
    if (stat.isDirectory()) {
      for (const child of fs.readdirSync(entry, { withFileTypes: true })) {
        if (child.name === ".git" || child.name === "node_modules" || child.name === "dist") {
          continue;
        }
        visit(path.join(entry, child.name));
      }
    } else if (stat.isFile()) {
      files.push(entry);
    }
  };
  entries.forEach(visit);
  return files.sort();
}

function usage() {
  return [
    "Usage: node audit-korean-terms.mjs [options] <file-or-directory>...",
    "",
    "Options:",
    "  --series <name>  Rule set (default: clinic-appointment)",
    "  --rules <path>   Rule JSON path",
    "  --json           Emit machine-readable findings",
    "  --help           Show this help",
  ].join("\n");
}

function renderText(findings, fileCount, series) {
  if (findings.length === 0) {
    return `Terminology audit passed: ${fileCount} file(s), series=${series}, findings=0.`;
  }
  const lines = findings.map((finding) => {
    const suggestion = finding.replacement ? `; prefer ${finding.replacement}` : "";
    return `${finding.file}:${finding.line}:${finding.column} [${finding.severity}] ${finding.ruleId}: ${finding.message} (found ${JSON.stringify(finding.match)}${suggestion})`;
  });
  return [`Terminology audit found ${findings.length} finding(s):`, ...lines].join("\n");
}

export function run(argv = process.argv.slice(2)) {
  const options = parseArgs(argv);
  if (options.help) {
    console.log(usage());
    return 0;
  }
  if (options.paths.length === 0) {
    throw new Error(`No input files were provided.\n\n${usage()}`);
  }

  const rules = loadRules(options.rulesPath);
  const files = collectFiles(options.paths);
  const findings = files.flatMap((file) =>
    auditText(fs.readFileSync(file, "utf8"), { file, series: options.series, rules }),
  );
  if (options.format === "json") {
    console.log(JSON.stringify({ series: options.series, files: files.length, findings }, null, 2));
  } else {
    console.log(renderText(findings, files.length, options.series));
  }
  return findings.some((finding) => finding.severity === "error") ? 1 : 0;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    process.exitCode = run();
  } catch (error) {
    console.error(`audit-korean-terms: ${error.message}`);
    process.exitCode = 2;
  }
}
