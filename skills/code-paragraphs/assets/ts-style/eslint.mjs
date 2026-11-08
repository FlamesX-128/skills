import js from "@eslint/js";

import prettier from "eslint-config-prettier";

import { defineConfig } from "eslint/config";

import functional from "eslint-plugin-functional";

import sonarjs from "eslint-plugin-sonarjs";

import tseslint from "typescript-eslint";

import { createSharedRules, documentationConfig } from "./rules.mjs";

const formattingRulesRequiredByStyle = new Set(["curly", "quotes"]);
const compatiblePrettierRules = Object.fromEntries(
    Object.entries(prettier.rules).filter(([rule]) => {
        return !formattingRulesRequiredByStyle.has(rule);
    }),
);

export const prettierCompatibleConfig = {
    ...prettier,
    name: "prettier-compatible-style-rules",
    rules: compatiblePrettierRules,
};

export function createProjectEslintConfig({
    files = ["**/*.{js,mjs,cjs,jsx,ts,tsx}"],
    ignores = [],
    globals = {},
    tsconfigRootDir = process.cwd(),
    thresholds,
    beforeBase = [],
    afterBase = [],
} = {}) {
    const sharedRules = createSharedRules(thresholds);

    return defineConfig(
        {
            ignores: ["**/node_modules/**", "**/dist/**", "**/.goal/**", ...ignores],
        },
        ...beforeBase,
        {
            files,
            extends: [
                js.configs.recommended,
                tseslint.configs.recommended,
                tseslint.configs.stylistic,
                sonarjs.configs.recommended,
                functional.configs.off,
            ],

            languageOptions: {
                globals,
                parserOptions: { tsconfigRootDir },
            },
            rules: sharedRules,
        },
        {
            files: ["**/*.ts"],
            rules: { "no-undef": "off" },
        },
        ...afterBase,
        documentationConfig,
        prettierCompatibleConfig,
    );
}
