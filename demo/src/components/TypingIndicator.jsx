export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-2" aria-label="Agent is typing">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 bg-slate-400 rounded-full"
          style={{ animation: `pulse-dot 1.4s infinite ${i * 0.2}s` }}
        />
      ))}
    </div>
  );
}
