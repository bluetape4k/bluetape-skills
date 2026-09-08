#!/usr/bin/env node

import assert from "node:assert/strict";
import { auditText, loadRules } from "./audit-korean-terms.mjs";

const rules = loadRules();

const clean = [
  "# 예약 운영",
  "빈시간에는 활성 제안만 남긴다.",
  "조치 메시지(작업 요청)는 저장된 명령을 다시 실행할 수 있는 상태로 남긴다.",
  "`PackageExecutionSnapshot`과 `snapshotHash`는 코드 식별자이므로 보존한다.",
].join("\n");

assert.deepEqual(auditText(clean, { file: "clean.mdx", rules }), []);

const bad = [
  "확정 방문 약속을 다시 해석하지 않는다.",
  "운영 화면의 계산 결과의 최신성 보장 문구를 고친다.",
  "조치 큐의 각 행에 다음 작업을 표시한다.",
  "스냅샷은 대기열(backlog)에 남는다.",
  "회원 circuit은 운영 보류 상태를 만든다.",
  "한 빈시간에는 활성 제안 하나만 남긴다.",
].join("\n");

const findings = auditText(bad, { file: "bad.mdx", rules });
assert.ok(findings.length >= 8, `expected repeated findings, got ${findings.length}`);
assert.ok(findings.some((finding) => finding.ruleId === "appointment-commitment"));
assert.ok(findings.some((finding) => finding.ruleId === "action-queue-row"));
assert.ok(findings.some((finding) => finding.ruleId === "snapshot-loanword"));

const codeOnly = "`스냅숏` `방문 약속` `회원 circuit`";
assert.deepEqual(auditText(codeOnly, { file: "code.mdx", rules }), []);

console.log(`audit-korean-terms tests passed: ${findings.length} intentional findings detected and code tokens ignored.`);
