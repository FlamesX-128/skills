import comments from "./comments.mjs";

// ! The custom comment rule is the sole fixer; the core rule rewrites protected block annotations.
export const shapeRules = {
    curly: ["error", "all"],
    "arrow-body-style": ["error", "always"],
    "@typescript-eslint/no-empty-function": ["error", { allow: ["arrowFunctions"] }],
    "padding-line-between-statements": [
        "error",
        { blankLine: "always", prev: "block-like", next: "*" },
    ],
    quotes: ["error", "double", { allowTemplateLiterals: false, avoidEscape: true }],
};

export const productRules = {
    "no-ternary": "error",
    "functional/no-loop-statements": "error",
    "functional/no-let": "error",
};

export const sonarRuleExceptions = {
    // ! Flat decisions are covered by no-ternary; nested conditionals stay readable.
    "sonarjs/no-nested-conditional": "off",
    // ! Interpolated templates are the standard form for URLs and messages.
    "sonarjs/no-nested-template-literals": "off",
    // ! TypeScript ESLint reports unused bindings without a duplicate Sonar diagnostic.
    "sonarjs/no-unused-vars": "off",
    // ! TypeScript ESLint reports unused imports without a duplicate Sonar diagnostic.
    "sonarjs/unused-import": "off",
    // ! Optional and explicit undefined differ under exactOptionalPropertyTypes.
    "sonarjs/no-redundant-optional": "off",
};

export const unusedBindingRules = {
    "@typescript-eslint/no-unused-vars": [
        "error",
        {
            args: "after-used",
            ignoreRestSiblings: true,
            argsIgnorePattern: "^_",
        },
    ],
};

export const documentationConfig = {
    plugins: { style: comments },
    rules: { "style/line-comments": "error" },
};

export const absoluteImports = [
    "error",
    {
        patterns: [
            {
                group: ["./**", "../**"],
                message: "Use the importing project's @/ source alias.",
            },
        ],
    },
];

export function createAliasConfigs({ sourceFiles = [], testFiles = [] } = {}) {
    const configs = [];
    if (sourceFiles.length > 0) {
        configs.push({
            files: sourceFiles,
            rules: { "no-restricted-imports": absoluteImports },
        });
    }

    if (testFiles.length > 0) {
        configs.push({
            files: testFiles,
            rules: {
                "no-restricted-imports": [
                    "error",
                    {
                        patterns: [
                            {
                                // ! @/ resolves only the importing project's source.
                                regex: "^(?:\\.\\./)+src/",
                                message: "Import this project's source through @/.",
                            },
                        ],
                    },
                ],
            },
        });
    }

    return configs;
}

export function createSharedRules(thresholds) {
    validateThresholds(thresholds);

    return {
        ...shapeRules,
        ...productRules,
        ...sonarRuleExceptions,
        ...unusedBindingRules,

        "sonarjs/cognitive-complexity": ["warn", thresholds.cognitiveComplexity],
        complexity: ["warn", thresholds.complexity],
        "max-depth": ["warn", thresholds.maxDepth],
        "max-params": ["warn", thresholds.maxParams],
        "max-lines-per-function": [
            "warn",
            {
                max: thresholds.maxLinesPerFunction,
                skipBlankLines: true,
                skipComments: true,
            },
        ],
    };
}

function validateThresholds(thresholds) {
    const names = [
        "complexity",
        "cognitiveComplexity",
        "maxDepth",
        "maxParams",
        "maxLinesPerFunction",
    ];

    const missing = names.filter((name) => {
        return !Number.isInteger(thresholds?.[name]) || thresholds[name] < 1;
    });

    if (missing.length > 0) {
        throw new Error(`Missing measured ESLint thresholds: ${missing.join(", ")}`);
    }
}
