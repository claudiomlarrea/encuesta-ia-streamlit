export function LessonMarkdown({ content }: { content: string }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none p-6">
      {content.split("\n").map((line, i) => {
        if (line.startsWith("# "))
          return (
            <h2 key={i} className="mb-2 mt-4 text-xl font-bold">
              {line.slice(2)}
            </h2>
          );
        if (line.startsWith("## "))
          return (
            <h3 key={i} className="mb-1 mt-3 text-lg font-semibold">
              {line.slice(3)}
            </h3>
          );
        if (line.startsWith("### "))
          return (
            <h4 key={i} className="mb-1 mt-2 text-base font-semibold">
              {line.slice(4)}
            </h4>
          );
        if (line.startsWith("> "))
          return (
            <blockquote
              key={i}
              className="my-2 border-l-4 border-[var(--aliaa-primary)] pl-4 italic text-[var(--aliaa-muted-foreground)]"
            >
              {line.slice(2)}
            </blockquote>
          );
        if (line.startsWith("```")) return null;
        if (line.startsWith("|"))
          return (
            <p key={i} className="font-mono text-xs">
              {line}
            </p>
          );
        if (line.startsWith("- "))
          return (
            <li key={i} className="ml-4 list-disc text-sm">
              {line.slice(2)}
            </li>
          );
        if (line.trim() === "") return <br key={i} />;
        return (
          <p key={i} className="text-sm leading-relaxed">
            {line}
          </p>
        );
      })}
    </div>
  );
}
