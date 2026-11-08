import assert from "node:assert/strict";

import { test } from "node:test";

import { ESLint } from "eslint";

import { format } from "prettier";

import { createProjectEslintConfig } from "./eslint.mjs";

import prettierOptions from "./prettier.mjs";

import { createAliasConfigs, createSharedRules } from "./rules.mjs";

// These limits describe only this small test corpus, not a consuming package.
const thresholds = {
    complexity: 2,
    cognitiveComplexity: 1,
    maxDepth: 1,
    maxParams: 1,
    maxLinesPerFunction: 10,
};

function linter({ fix = false, extra = [] } = {}) {
    return new ESLint({
        overrideConfigFile: true,
        overrideConfig: createProjectEslintConfig({
            thresholds,
            afterBase: extra,
        }),
        fix,
    });
}

test("shared configuration enforces decisions, loops, mutation and code shape", async () => {
    const [result] = await linter().lintText(
        [
            "export const choice = true ? 1 : 2;",
            "let index = 0;",
            "for (const item of [choice]) { index += item; }",
            "if (index) index++;",
            "export const read = () => index;",
            "export const label = `plain`;",
        ].join("\n"),
        { filePath: "fixture.ts" },
    );
    assert.equal(result.fatalErrorCount, 0);
    const rules = new Set(
        result.messages.map((message) => {
            return message.ruleId;
        }),
    );
    [
        "no-ternary",
        "functional/no-loop-statements",
        "functional/no-let",
        "curly",
        "arrow-body-style",
        "quotes",
    ].forEach((rule) => {
        assert.ok(rules.has(rule), rule);
    });
});

test("Prettier and ESLint reach a stable result without erasing paragraphs", async () => {
    const input = [
        "export function classify(value: boolean) {",
        'if (value) return "yes";',
        "",
        'return "no";',
        "}",
    ].join("\n");
    const formatted = await format(input, { ...prettierOptions, parser: "typescript" });
    const fixer = linter({ fix: true });
    const [first] = await fixer.lintText(formatted, { filePath: "fixture.ts" });
    assert.deepEqual(first.messages, []);
    const settled = await format(first.output ?? formatted, {
        ...prettierOptions,
        parser: "typescript",
    });
    const [second] = await fixer.lintText(settled, { filePath: "fixture.ts" });
    assert.equal(second.output, undefined);
    assert.deepEqual(second.messages, []);
    assert.match(settled, /}\n\n    return/);
});

test("shared autofix preserves protected block annotations", async () => {
    const fixer = linter({ fix: true });
    const comments = [
        "/*! Copyright Example\n * Preserve this license.\n */",
        "/*# sourceMappingURL=app.js.map\n */",
        "/* @__PURE__\n */",
        "/* @ts-check\n */",
    ];

    await Promise.all(
        comments.map(async (comment) => {
            const input = `${comment}\nexport const value = 1;\n`;
            const [result] = await fixer.lintText(input, { filePath: "fixture.js" });
            assert.equal(result.fatalErrorCount, 0);
            assert.equal(result.output ?? input, input);
        }),
    );
});

test("alias restriction applies to source but allows local test helpers", async () => {
    const checker = linter({
        extra: createAliasConfigs({
            sourceFiles: ["src/**/*.ts"],
            testFiles: ["test/**/*.ts"],
        }),
    });
    const cases = [
        ["src/fixture.ts", "./value.js", true],
        ["test/fixture.ts", "./helper.js", false],
        ["test/fixture.ts", "../src/value.js", true],
        ["src/fixture.ts", "@/value.js", false],
    ];

    await Promise.all(
        cases.map(async ([filePath, specifier, restricted]) => {
            const [result] = await checker.lintText(
                `import { value } from "${specifier}";\n\nexport { value };\n`,
                { filePath },
            );
            assert.equal(result.fatalErrorCount, 0);
            assert.equal(
                result.messages.some((message) => {
                    return message.ruleId === "no-restricted-imports";
                }),
                restricted,
                `${filePath}: ${specifier}`,
            );
        }),
    );
});

test("thresholds require an explicit positive integer for every metric", () => {
    assert.throws(() => {
        createSharedRules();
    }, /Missing measured/);
    assert.throws(() => {
        createSharedRules({ ...thresholds, maxDepth: 0 });
    }, /maxDepth/);
    assert.throws(() => {
        createSharedRules({ ...thresholds, maxParams: 1.5 });
    }, /maxParams/);
    assert.doesNotThrow(() => {
        createSharedRules(thresholds);
    });
});

test("tagged JavaScript types remain while prose blocks convert", async () => {
    const input = [
        "/** @type {number} */",
        "export const value = 1;",
        "",
        "/* Reason for the next value. */",
        "export const next = 2;",
        "",
    ].join("\n");
    const [result] = await linter({ fix: true }).lintText(input, { filePath: "fixture.js" });
    assert.deepEqual(result.messages, []);
    assert.ok(result.output.includes("/** @type {number} */"));
    assert.ok(result.output.includes("// Reason for the next value."));
});
