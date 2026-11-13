import type { ReactElement } from "react";

export type LibItem = { name: string; code: string; el: ReactElement };
export type LibGroup = { id: string; title: string; items: LibItem[] };

export const li = (name: string, code: string, el: ReactElement): LibItem => ({
  name,
  code,
  el,
});
