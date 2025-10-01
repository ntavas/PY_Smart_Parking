import type {PropsWithChildren} from "react";

/**
 * Small rounded label for categories/filters/status.
 * - Dark mode supported
 * - Children define the label text/content
 */
export default function Badge({ children }: PropsWithChildren) {
    return (
        <span className="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-200">
      {children}
    </span>
    );
}
