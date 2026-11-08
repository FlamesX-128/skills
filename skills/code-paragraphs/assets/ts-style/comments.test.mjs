import assert from "node:assert/strict";

import { test } from "node:test";

import { Linter } from "eslint";

import comments from "./comments.mjs";

const linter = new Linter();
const config = [{ plugins: { style: comments }, rules: { "style/line-comments": "error" } }];

function activeConfig(comment) {
    if (comment.includes("eslint-disable")) {
        return [...config, { rules: { "no-console": "error" } }];
    }

    return config;
}

test("description-only JSDoc and banners become line comments", () => {
    const input =
        "/** Description without tags. */\nconst first = 1;\n/* Banner */\nconst second = 2;\n";

    const result = linter.verifyAndFix(input, config);

    assert.equal(result.messages.length, 0);
    assert.equal(
        result.output,
        "// Description without tags.\nconst first = 1;\n// Banner\nconst second = 2;\n",
    );
});

test("typed and tagged documentation remains unchanged", () => {
    const input =
        "/** Description.\n * @param input Actual parameter\n * @returns Its result\n */\nfunction read(input) { return input; }\n/** @type {number} */\nconst number = 1;";

    const result = linter.verifyAndFix(input, config);

    assert.equal(result.messages.length, 0);
    assert.equal(result.output, input);
});

test("protected compiler, linter, bundler and license comments stay intact", () => {
    const cases = [
        ["/*#__PURE__*/", "const value = create();"],
        ["/*! Copyright (c) Example */", "const value = 1;"],
        ["/* eslint-disable no-console */", "console.log(value);"],
        ["/* @ts-expect-error legacy */", "const value = create();"],
        ["/*# sourceMappingURL=app.js.map */", "const value = 1;"],
    ];

    cases.forEach(([comment, body]) => {
        const input = `${comment}\n${body}`;
        const result = linter.verifyAndFix(input, activeConfig(comment));

        assert.equal(result.messages.length, 0, comment);
        assert.equal(result.output, input, comment);
    });
});

test("unknown documentation tags are reported without rewriting the comment", () => {
    const input = "/** Description.\n * @custom unsupported\n */\nfunction value() {}";

    const result = linter.verifyAndFix(input, config);

    assert.equal(result.fixed, false);
    assert.equal(result.output, input);
    assert.match(result.messages[0].message, /Unsupported documentation tag: @custom/);
});

test("an inline block is reported without an unsafe ASI fix", () => {
    const input = "function value() { return /* explanatory */ 1; }";
    const result = linter.verifyAndFix(input, config);

    assert.equal(result.messages.length, 1);
    assert.equal(result.fixed, false);
    assert.equal(result.output, input);
});

test("an email inside description text is not a documentation tag", () => {
    const result = linter.verifyAndFix(
        "/** Contact user@example.test */\nconst value = 1;",
        config,
    );

    assert.equal(result.messages.length, 0);
    assert.ok(result.output.startsWith("// Contact user@example.test"));
});
