const documentationTags = new Set([
    "defaultValue",
    "deprecated",
    "example",
    "internal",
    "param",
    "returns",
    "see",
    "throws",
    "type",
]);

function documentationTagNames(value) {
    return value.split(/\r?\n/).flatMap((line) => {
        const candidate = line.trimStart().replace(/^\*\s?/, "");
        const match = /^@(\w+)/.exec(candidate);

        if (match) {
            return [match[1]];
        }

        return [];
    });
}

function unsupportedDocumentationTags(comment) {
    if (!comment.value.startsWith("*")) {
        return [];
    }

    return documentationTagNames(comment.value).filter((tag) => {
        return !documentationTags.has(tag);
    });
}

function isProtectedComment(comment) {
    const value = comment.value.trimStart();

    return (
        value.startsWith("!") ||
        /^(?:eslint(?:-|\b)|@ts-(?:check|nocheck|ignore|expect-error)\b)/i.test(value) ||
        /^[@#](?:__\w+__|\s*source(?:MappingURL|URL)\s*=)/i.test(value) ||
        /^@(license|preserve|copyright|vite-ignore|vite-preload)\b/i.test(value)
    );
}

function unsupportedTagMessage(tags) {
    if (tags.length === 1) {
        return `Unsupported documentation tag: @${tags[0]}.`;
    }

    const names = tags.map((tag) => {
        return `@${tag}`;
    });

    return `Unsupported documentation tags: ${names.join(", ")}.`;
}

function lineComment(line) {
    if (line) {
        return `// ${line}`;
    }

    return "//";
}

function commentLines(value) {
    return value
        .split(/\r?\n/)
        .map((line) => {
            return line.trim().replace(/^\*\s?/, "");
        })
        .join("\n")
        .trim()
        .split("\n")
        .map(lineComment);
}

function fixBlockComment(source, comment, fixer) {
    const before = source.lines[comment.loc.start.line - 1].slice(0, comment.loc.start.column);

    const after = source.lines[comment.loc.end.line - 1].slice(comment.loc.end.column);

    // ! Inline comments can separate return from its value; moving them needs review.
    if (before.trim() || after.trim()) {
        return null;
    }

    return fixer.replaceText(comment, commentLines(comment.value).join(`\n${before}`));
}

export default {
    rules: {
        "line-comments": {
            meta: {
                type: "layout",
                docs: {
                    description: "Line comments, or JSDoc with actual documentation tags",
                },

                schema: [],
                fixable: "whitespace",
                messages: {
                    line: "Use // comments; reserve JSDoc for documentation with tags.",
                },
            },

            create(context) {
                const source = context.sourceCode;

                return {
                    Program() {
                        source.getAllComments().forEach((comment) => {
                            if (comment.type !== "Block" || isProtectedComment(comment)) {
                                return;
                            }

                            const unsupportedTags = unsupportedDocumentationTags(comment);

                            if (unsupportedTags.length > 0) {
                                context.report({
                                    loc: comment.loc,
                                    message: unsupportedTagMessage(unsupportedTags),
                                });

                                return;
                            }

                            if (
                                comment.value.startsWith("*") &&
                                documentationTagNames(comment.value).length > 0
                            ) {
                                return;
                            }

                            context.report({
                                loc: comment.loc,
                                messageId: "line",

                                fix(fixer) {
                                    return fixBlockComment(source, comment, fixer);
                                },
                            });
                        });
                    },
                };
            },
        },
    },
};
