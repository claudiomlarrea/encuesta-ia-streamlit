"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { ChevronLeft, ChevronRight, Volume2, VolumeX, Pause, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Slide {
  title: string;
  bullets?: string[];
  narration: string;
  highlight?: string;
  audio?: string;
}

interface PresentationData {
  format: "presentation";
  slides: Slide[];
}

export function parsePresentation(content: string | null): PresentationData | null {
  if (!content) return null;
  try {
    const data = JSON.parse(content);
    if (data.format === "presentation" && Array.isArray(data.slides)) return data;
  } catch {
    return null;
  }
  return null;
}

interface PresentationPlayerProps {
  content: string;
  lessonTitle: string;
  /** Inicia reproducción continua al montar (p. ej. al pasar de lección automáticamente) */
  autoStart?: boolean;
  /** Se llama al terminar el audio del último slide con reproducción continua activa */
  onComplete?: () => void;
  onAutoStartConsumed?: () => void;
}

export function PresentationPlayer({
  content,
  lessonTitle,
  autoStart = false,
  onComplete,
  onAutoStartConsumed,
}: PresentationPlayerProps) {
  const data = parsePresentation(content);
  const [current, setCurrent] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const SLIDE_PAUSE_MS = 900;

  const slides = data?.slides ?? [];
  const slide = slides[current];
  const hasAudio = !!slide?.audio;

  const advanceAfterSlide = useCallback(() => {
    if (current < slides.length - 1) {
      setTimeout(() => setCurrent((c) => c + 1), SLIDE_PAUSE_MS);
    } else {
      onComplete?.();
    }
  }, [current, slides.length, onComplete]);

  const stopAudio = useCallback(() => {
    const el = audioRef.current;
    if (el) {
      el.pause();
      el.currentTime = 0;
    }
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    setPlaying(false);
  }, []);

  const speakWithTTS = useCallback((text: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const voices = window.speechSynthesis.getVoices();
    const spanish =
      voices.find((v) => v.lang.startsWith("es")) ?? voices[0];
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-MX";
    utterance.rate = 0.82;
    if (spanish) utterance.voice = spanish;
    utterance.onend = () => {
      setPlaying(false);
      if (autoPlay) advanceAfterSlide();
    };
    utterance.onerror = () => setPlaying(false);
    setPlaying(true);
    window.speechSynthesis.speak(utterance);
    // Chrome bug: resume after speak
    window.speechSynthesis.resume();
  }, [autoPlay, advanceAfterSlide]);

  const playNarration = useCallback(() => {
    if (!slide) return;
    stopAudio();

    if (slide.audio && audioRef.current) {
      audioRef.current.src = slide.audio;
      audioRef.current.play().then(() => setPlaying(true)).catch(() => {
        speakWithTTS(slide.narration);
      });
    } else {
      speakWithTTS(slide.narration);
    }
  }, [slide, stopAudio, speakWithTTS]);

  useEffect(() => {
    return () => stopAudio();
  }, [stopAudio]);

  useEffect(() => {
    setCurrent(0);
    setPlaying(false);
    setAutoPlay(false);
    stopAudio();
  }, [content, lessonTitle, stopAudio]);

  useEffect(() => {
    if (!autoStart) return;
    setAutoPlay(true);
    const t = setTimeout(() => {
      playNarration();
      onAutoStartConsumed?.();
    }, 400);
    return () => clearTimeout(t);
  }, [autoStart]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (current === 0) return;
    stopAudio();
    if (autoPlay && slide) {
      const t = setTimeout(playNarration, 300);
      return () => clearTimeout(t);
    }
  }, [current, autoPlay]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!data || !slide) return null;

  return (
    <div className="overflow-hidden rounded-t-xl bg-gradient-to-br from-slate-900 via-blue-950 to-teal-900">
      <audio
        ref={audioRef}
        onEnded={() => {
          setPlaying(false);
          if (autoPlay) advanceAfterSlide();
        }}
        onError={() => setPlaying(false)}
        preload="auto"
      />

      <div className="flex aspect-video flex-col p-6 sm:p-10">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-blue-500 text-xs font-bold text-white">
              A
            </div>
            <span className="text-xs font-medium text-blue-200">ALIAA · {lessonTitle}</span>
          </div>
          <span className="text-xs text-blue-300">
            {current + 1} / {slides.length}
          </span>
        </div>

        <div className="flex flex-1 flex-col justify-center">
          <h2 className="mb-4 text-xl font-bold text-white sm:text-2xl lg:text-3xl">
            {slide.title}
          </h2>
          {slide.highlight && (
            <p className="mb-4 text-lg font-medium text-teal-300">{slide.highlight}</p>
          )}
          {slide.bullets && (
            <ul className="space-y-2">
              {slide.bullets.map((b, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-blue-100 sm:text-base">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-400" />
                  {b}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-4 rounded-lg bg-black/30 p-3">
          <p className="text-xs leading-relaxed text-blue-200/80 sm:text-sm">
            {slide.narration.split(/(?<=[.!?])\s+/).map((sentence, i) => (
              <span key={i} className="block py-0.5">
                {sentence}
              </span>
            ))}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-black/40 px-4 py-3">
        <div className="flex gap-1">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => { stopAudio(); setCurrent(i); }}
              className={cn(
                "h-1.5 rounded-full transition-all",
                i === current ? "w-6 bg-teal-400" : "w-1.5 bg-white/30"
              )}
            />
          ))}
        </div>

        <Button
          size="sm"
          className="bg-teal-500 text-white hover:bg-teal-600"
          onClick={() => {
            if (playing) {
              stopAudio();
              setAutoPlay(false);
            } else {
              setAutoPlay(true);
              playNarration();
            }
          }}
        >
          {playing ? (
            <><VolumeX className="mr-2 h-4 w-4" /> Detener</>
          ) : (
            <><Volume2 className="mr-2 h-4 w-4" /> Escuchar lección</>
          )}
        </Button>

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            className="text-white hover:bg-white/10"
            onClick={() => { stopAudio(); setCurrent((c) => Math.max(0, c - 1)); }}
            disabled={current === 0}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-white hover:bg-white/10"
            onClick={() => {
              if (autoPlay) { setAutoPlay(false); stopAudio(); }
              else { setAutoPlay(true); playNarration(); }
            }}
          >
            {autoPlay ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-white hover:bg-white/10"
            onClick={() => { stopAudio(); setCurrent((c) => Math.min(slides.length - 1, c + 1)); }}
            disabled={current === slides.length - 1}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {!hasAudio && (
        <p className="bg-amber-900/40 px-4 py-1 text-center text-xs text-amber-200">
          Ejecutá <code className="rounded bg-black/30 px-1">npm run generate:audio</code> para audio HD
        </p>
      )}
    </div>
  );
}
