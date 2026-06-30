import next from "eslint-config-next";

/**
 * Flat ESLint config. eslint-config-next (v16+) exports a ready-to-use flat
 * config array (Next + React + hooks + a11y + import + TypeScript), so we spread
 * it directly — no FlatCompat needed.
 */
const eslintConfig = [
  ...next,
  {
    ignores: [".next/**", "node_modules/**", "next-env.d.ts"],
  },
];

export default eslintConfig;
