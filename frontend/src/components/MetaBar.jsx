import React from "react";

export function TopMetaBar({ section, index, total }) {
  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-line bg-base-950">
      <div className="meta-label text-[11px] text-ink-muted flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-teal-accent inline-block" />
        StackSmashers &middot; EdgeHealth
      </div>
      {section && (
        <div className="meta-label text-[11px] text-cyan-accent">{section}</div>
      )}
      {index && total && (
        <div className="meta-label text-[11px] text-ink-muted">
          {String(index).padStart(2, "0")} / {String(total).padStart(2, "0")}
        </div>
      )}
    </div>
  );
}

export function BottomMetaBar({ items = [] }) {
  return (
    <div className="px-6 py-3 border-t border-line bg-base-950">
      <div className="meta-label text-[10px] text-ink-muted">
        {items.join("   \u00b7   ")}
      </div>
    </div>
  );
}