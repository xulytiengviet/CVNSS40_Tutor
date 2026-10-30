'use strict';
const fs = require('node:fs');
const converter = require('./cvnss-converter.js');
try {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const op = input.operation;
  const text = input.text ?? '';
  let result;
  if (op === 'convert') result = converter.convert(text, input.mode ?? 'cqn');
  else if (op === 'inspect') result = converter.inspectWord(text, input.source ?? 'cvss');
  else if (op === 'candidates') result = {input: text, source: input.source ?? 'cvss', candidates: converter.candidatesForWord(text, input.source ?? 'cvss')};
  else if (op === 'audit') result = converter.audit();
  else if (op === 'self_test') result = converter.selfTest();
  else throw new Error('Unknown operation');
  process.stdout.write(JSON.stringify(result));
} catch (error) {
  process.stderr.write(String(error && error.message || error));
  process.exitCode = 1;
}
