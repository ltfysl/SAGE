import { actionsGroups } from "./actions";
import { formsGroups } from "./forms";
import { feedbackGroups } from "./feedback";
import { dataGroups } from "./data";
import { navGroups } from "./nav";
import { surfaceGroups } from "./surfaces";
import { typographyGroups } from "./typography";
import { miscGroups } from "./misc";
import type { LibGroup } from "./types";

export const library: LibGroup[] = [
  ...actionsGroups,
  ...formsGroups,
  ...feedbackGroups,
  ...dataGroups,
  ...navGroups,
  ...surfaceGroups,
  ...typographyGroups,
  ...miscGroups,
];

export const libraryCount = library.reduce((n, g) => n + g.items.length, 0);
