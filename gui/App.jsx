import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";

/**
 * TranscribeMonkey – Frontend-only prototype
 * Goal: Lock the UX and component layout before wiring any backend.
 * Tech: React + Tailwind. No real API calls yet. Handlers are stubs.
 *
 * Core screens:
 * - Source input (YouTube URL | Local file drop)
 * - Status & Model panel (CUDA, Whisper model, Translator)
 * - Actions (Download & Transcribe, Transcribe File, Stop, Open Folder)
 * - Live Progress with stages and ETA
 * - Output preview (SRT/VTT/TXT)
 * - Settings modal with tabs (General, Process, Output, About)
 */

// ------------------------- Helpers & Mock Types -------------------------
const STAGES = [
  "Model Download",
  "Download",
  "Chunking",
  "Transcription",
  "Translation",
] as const;

const MODEL_VARIANTS = ["tiny", "base", "small", "medium", "large"] as const;
const OUTPUT_FORMATS = ["srt", "vtt", "txt"] as const;
const LANGS = ["auto", "en", "nl", "de", "fr", "es", "it", "pl", "pt", "ru", "ja", "zh"];

function classNames(...s) { return s.filter(Boolean).join(" "); }

// ------------------------------ Root UI ------------------------------
export default function App() {
  const [theme, setTheme] = useState("dark");
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <header className="sticky top-0 z-20 border-b border-zinc-200/50 dark:border-zinc-800/50 backdrop-blur bg-white/60 dark:bg-zinc-950/60">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MonkeyLogo />
            <div>
              <h1 className="text-xl font-bold tracking-tight">TranscribeMonkey</h1>
              <p className="text-xs text-zinc-500">Download · Transcribe · Translate</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
              className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <SettingsButton />
            <HelpButton />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 space-y-6">
          <SourceCard />
          <ActionsAndProgressCard />
          <OutputPreviewCard />
        </section>

        <aside className="space-y-6">
          <SystemStatusCard />
          <ModelManagerCard />
          <LogsCard />
        </aside>
      </main>

      <Footer />
      <SettingsModalPortal />
    </div>
  );
}

// ------------------------------ Header Bits ------------------------------
function MonkeyLogo() {
  return (
    <motion.div
      initial={{ rotate: -6, scale: 0.9 }}
      animate={{ rotate: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 180, damping: 14 }}
      className="size-10 grid place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-600 text-white shadow"
    >
      🐒
    </motion.div>
  );
}

function HelpButton() {
  return (
    <button
      className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900"
      onClick={() => alert("Docs coming soon. This is a frontend-only prototype.")}
    >
      Help
    </button>
  );
}

// ------------------------------ Global Stores ------------------------------
// In real app, move to context/store (Zustand/Redux). Using module-level for brevity.
const useGlobal = createGlobalStore();

function createGlobalStore() {
  // crude global state hook
  const store = {
    /** @type {ReturnType<typeof React.useState<string>>} */ _lang: null,
  };
  return function useGlobal() {
    const [youtubeUrl, setYoutubeUrl] = useState("");
    const [file, setFile] = useState(null); // File | null

    const [config, setConfig] = useState({
      chunk_length: 30,
      model_variant: "small",
      language: "auto",
      output_format: "srt",
      output_directory: "~/TranscribeMonkey",
      delete_temp_files: true,
      translate: false,
      target_language: "en",
      show_system_status: true,
      normalize_audio: true,
      reduce_noise: false,
      trim_silence: false,
    });

    const [status, setStatus] = useState({
      cuda: "unknown", // "available" | "cpu" | "unknown"
      whisperModelInstalled: false,
      translatorAvailable: true,
    });

    const [job, setJob] = useState({
      running: false,
      stage: null, // keyof STAGES | null
      percent: 0,
      idx: 0,
      total: 0,
      eta: "--:--",
      currentLanguage: "auto",
      cancellable: false,
      finished: false,
      error: null,
    });

    const [modelDl, setModelDl] = useState({
      inProgress: false,
      variant: "small",
      percent: 0,
      error: null,
    });

    const [output, setOutput] = useState({
      activeTab: "srt",
      srt: "",
      vtt: "",
      txt: "",
    });

    const [logs, setLogs] = useState([
      "TranscribeMonkey booted",
      "Checking environment…",
    ]);

    const appendLog = (line) => setLogs((ls) => [...ls, line]);

    // Mocked environment checks
    const checkCuda = () => {
      appendLog("CUDA check triggered");
      setStatus((s) => ({ ...s, cuda: Math.random() > 0.5 ? "available" : "cpu" }));
    };

    const checkModel = () => {
      appendLog(`Checking whisper model: ${config.model_variant}`);
      setStatus((s) => ({ ...s, whisperModelInstalled: Math.random() > 0.4 }));
    };

    const startModelDownload = () => {
      if (modelDl.inProgress) return;
      appendLog(`Downloading model: ${config.model_variant}`);
      setModelDl({ inProgress: true, variant: config.model_variant, percent: 0, error: null });
      const start = Date.now();
      const timer = setInterval(() => {
        setModelDl((m) => {
          const np = Math.min(100, m.percent + 5 + Math.random() * 12);
          if (np >= 100) {
            clearInterval(timer);
            appendLog("Model download finished");
            setStatus((s) => ({ ...s, whisperModelInstalled: true }));
            return { ...m, inProgress: false, percent: 100 };
          }
          return { ...m, percent: np };
        });
      }, 400);
    };

    const startJob = (kind) => {
      // kind: "yt" | "file"
      if (job.running) return;
      setOutput({ activeTab: config.output_format, srt: "", vtt: "", txt: "" });
      setJob({ running: true, stage: STAGES[0], percent: 0, idx: 0, total: 100, eta: "--:--", currentLanguage: config.language, cancellable: true, finished: false, error: null });
      appendLog(`Job started via ${kind === "yt" ? "YouTube URL" : "local file"}`);

      // Fake stage progression
      const perStage = 100 / STAGES.length;
      let stageIdx = 0;
      const timer = setInterval(() => {
        setJob((j) => {
          let percent = j.percent + Math.random() * 6 + 4;
          let s = j.stage;
          if (percent >= (stageIdx + 1) * perStage && stageIdx < STAGES.length - 1) {
            stageIdx += 1;
            s = STAGES[stageIdx];
            appendLog(`Stage → ${s}`);
          }
          if (percent >= 100) {
            clearInterval(timer);
            const mockSrt = makeMockSRT();
            appendLog("Job finished");
            setOutput({ activeTab: config.output_format, srt: mockSrt, vtt: toVTT(mockSrt), txt: stripSRT(mockSrt) });
            return { ...j, running: false, percent: 100, stage: null, eta: "00:00", finished: true, cancellable: false };
          }
          return { ...j, percent: Math.min(99, percent), stage: s, eta: estimateETA(percent) };
        });
      }, 500);
    };

    const cancelJob = () => {
      if (!job.running) return;
      setJob((j) => ({ ...j, running: false, cancellable: false, error: "Cancelled by user", stage: null }));
      appendLog("Job cancelled by user");
    };

    const openOutputFolder = () => {
      appendLog(`Open output folder: ${config.output_directory}`);
      alert("Would open output folder via backend. Stub in prototype.");
    };

    return {
      youtubeUrl, setYoutubeUrl,
      file, setFile,
      config, setConfig,
      status, setStatus,
      job, setJob,
      output, setOutput,
      logs, appendLog,
      modelDl, setModelDl,
      // actions
      checkCuda, checkModel, startModelDownload,
      startJob, cancelJob, openOutputFolder,
    };
  };
}

// ------------------------------ Cards ------------------------------
function Card({ title, actions, children }) {
  return (
    <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/60 dark:bg-zinc-900/60 backdrop-blur shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-100 dark:border-zinc-800">
        <h2 className="text-sm font-semibold tracking-tight">{title}</h2>
        <div className="flex items-center gap-2">{actions}</div>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

function SourceCard() {
  const g = useGlobal();
  const [tab, setTab] = useState("yt");
  const fileInputRef = useRef(null);

  return (
    <Card
      title="Input source"
      actions={
        <div className="inline-flex rounded-xl bg-zinc-100 dark:bg-zinc-800 p-1">
          <TabBtn active={tab === "yt"} onClick={() => setTab("yt")}>YouTube</TabBtn>
          <TabBtn active={tab === "file"} onClick={() => setTab("file")}>Local file</TabBtn>
        </div>
      }
    >
      {tab === "yt" ? (
        <div className="space-y-3">
          <label className="text-sm text-zinc-500">YouTube URL</label>
          <input
            type="url"
            placeholder="https://www.youtube.com/watch?v=…"
            value={g.youtubeUrl}
            onChange={(e) => g.setYoutubeUrl(e.target.value)}
            className="w-full rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
          <p className="text-xs text-zinc-500">Uses yt-dlp to fetch audio. Will auto-convert to 16kHz mono WAV.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const f = e.dataTransfer.files?.[0];
              if (f) g.setFile(f);
            }}
            className={classNames(
              "grid place-items-center rounded-2xl border-2 border-dashed px-6 py-10 cursor-pointer",
              g.file ? "border-emerald-400/70 bg-emerald-50/50 dark:bg-emerald-900/10" : "border-zinc-300/80 dark:border-zinc-700/80 hover:bg-zinc-50 dark:hover:bg-zinc-900"
            )}
          >
            <div className="text-center">
              <div className="text-3xl">📁</div>
              <div className="mt-2 font-medium">{g.file ? g.file.name : "Drop audio/video here or click to select"}</div>
              <div className="text-xs text-zinc-500">MP3, WAV, MP4, MKV…</div>
            </div>
            <input ref={fileInputRef} type="file" className="hidden" onChange={(e) => g.setFile(e.target.files?.[0] ?? null)} />
          </div>
          <div className="text-xs text-zinc-500">Audio is converted to 16kHz mono WAV before chunking.</div>
        </div>
      )}
    </Card>
  );
}

function ActionsAndProgressCard() {
  const g = useGlobal();
  const disabledYT = !g.youtubeUrl || g.job.running;
  const disabledFile = !g.file || g.job.running;

  return (
    <Card
      title="Run"
      actions={
        <div className="flex gap-2">
          <button
            className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900"
            onClick={() => openSettingsModal()}
          >
            Settings
          </button>
          <button
            className="px-3 py-1.5 text-sm rounded-xl border border-amber-500 text-amber-700 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/40"
            onClick={() => g.openOutputFolder()}
          >
            Open Output Folder
          </button>
        </div>
      }
    >
      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <div className="flex gap-2">
            <button
              disabled={disabledYT}
              onClick={() => g.startJob("yt")}
              className={classNames(
                "flex-1 rounded-xl px-4 py-2 font-medium",
                disabledYT ? "bg-zinc-200 dark:bg-zinc-800 text-zinc-500" : "bg-amber-500 text-white hover:bg-amber-600"
              )}
            >
              Download & Transcribe
            </button>
            <button
              disabled={disabledFile}
              onClick={() => g.startJob("file")}
              className={classNames(
                "flex-1 rounded-xl px-4 py-2 font-medium",
                disabledFile ? "bg-zinc-200 dark:bg-zinc-800 text-zinc-500" : "bg-emerald-500 text-white hover:bg-emerald-600"
              )}
            >
              Transcribe File
            </button>
          </div>
          <div className="flex gap-2">
            <button
              disabled={!g.job.cancellable}
              onClick={g.cancelJob}
              className={classNames(
                "flex-1 rounded-xl px-4 py-2 font-medium",
                g.job.cancellable ? "bg-red-500 text-white hover:bg-red-600" : "bg-zinc-200 dark:bg-zinc-800 text-zinc-500"
              )}
            >
              Stop
            </button>
            <button
              onClick={() => alert("Queue support to be added. Stub.")}
              className="flex-1 rounded-xl px-4 py-2 font-medium border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900"
            >
              Queue Later
            </button>
          </div>
          {g.job.error && (
            <div className="text-sm text-red-500">{g.job.error}</div>
          )}
        </div>

        <div className="space-y-3">
          <ProgressStage stage={g.job.stage} percent={g.job.percent} />
          <div className="grid grid-cols-3 gap-2 text-xs text-zinc-500">
            <InfoTile label="ETA" value={g.job.eta} />
            <InfoTile label="Language" value={g.job.currentLanguage} />
            <InfoTile label="Status" value={g.job.finished ? "Done" : g.job.running ? "Running" : "Idle"} />
          </div>
        </div>
      </div>
    </Card>
  );
}

function ProgressStage({ stage, percent }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs">
        <span className="text-zinc-500">{stage || "Ready"}</span>
        <span className="font-medium">{Math.floor(percent)}%</span>
      </div>
      <div className="h-3 w-full rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(100, Math.floor(percent))}%` }}
          transition={{ type: "spring", stiffness: 120, damping: 20 }}
          className="h-full bg-gradient-to-r from-amber-400 to-orange-600"
        />
      </div>
      <div className="flex items-center gap-2 mt-2">
        {STAGES.map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={classNames(
              "size-2 rounded-full",
              stage === s ? "bg-amber-500" : "bg-zinc-400 dark:bg-zinc-600"
            )} />
            <span className="text-[11px] text-zinc-500">{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function InfoTile({ label, value }) {
  return (
    <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 px-3 py-2 bg-white/40 dark:bg-zinc-900/40">
      <div className="text-zinc-500">{label}</div>
      <div className="font-medium text-zinc-900 dark:text-zinc-100">{value}</div>
    </div>
  );
}

function OutputPreviewCard() {
  const g = useGlobal();
  const tabs = [
    { id: "srt", label: "SRT" },
    { id: "vtt", label: "VTT" },
    { id: "txt", label: "TXT" },
  ];

  const active = g.output.activeTab;
  const text = g.output[active] || placeholderOutput(active);

  return (
    <Card
      title="Output preview"
      actions={
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-xl bg-zinc-100 dark:bg-zinc-800 p-1">
            {tabs.map((t) => (
              <TabBtn key={t.id} active={active === t.id} onClick={() => g.setOutput((o) => ({ ...o, activeTab: t.id }))}>{t.label}</TabBtn>
            ))}
          </div>
          <button onClick={() => navigator.clipboard.writeText(text)} className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Copy</button>
          <button onClick={() => alert("Save As… handled by backend later")} className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Save As</button>
        </div>
      }
    >
      <div className="h-60 overflow-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white/40 dark:bg-zinc-900/40 p-3 font-mono text-[13px] leading-relaxed whitespace-pre-wrap">
        {text}
      </div>
    </Card>
  );
}

function SystemStatusCard() {
  const g = useGlobal();
  return (
    <Card
      title="System status"
      actions={
        <button onClick={() => { g.checkCuda(); g.checkModel(); }} className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Check</button>
      }
    >
      <div className="flex flex-wrap gap-2">
        <StatusPill
          label="CUDA"
          state={g.status.cuda === "available" ? "ok" : g.status.cuda === "cpu" ? "warn" : "idle"}
          detail={g.status.cuda === "available" ? "GPU ready" : g.status.cuda === "cpu" ? "CPU only" : "Unknown"}
        />
        <StatusPill
          label="Whisper model"
          state={g.status.whisperModelInstalled ? "ok" : "warn"}
          detail={g.status.whisperModelInstalled ? `${g.config.model_variant} present` : "Missing"}
        />
        <StatusPill
          label="Translator"
          state={g.status.translatorAvailable ? "ok" : "warn"}
          detail={g.status.translatorAvailable ? "Available" : "Unavailable"}
        />
      </div>
      {g.status.whisperModelInstalled ? null : (
        <div className="mt-3 text-xs text-zinc-500">Model not installed. Use the Model panel to download.</div>
      )}
    </Card>
  );
}

function StatusPill({ label, state, detail }) {
  const color = state === "ok" ? "bg-emerald-500" : state === "warn" ? "bg-amber-500" : "bg-zinc-400";
  return (
    <div className="flex items-center gap-2 rounded-full border border-zinc-200 dark:border-zinc-800 px-3 py-1 bg-white/40 dark:bg-zinc-900/40">
      <span className={classNames("size-2 rounded-full", color)} />
      <span className="text-sm font-medium">{label}</span>
      <span className="text-xs text-zinc-500">{detail}</span>
    </div>
  );
}

function ModelManagerCard() {
  const g = useGlobal();
  return (
    <Card title="Model" actions={null}>
      <div className="space-y-3">
        <div>
          <label className="text-sm text-zinc-500">Variant</label>
          <select
            value={g.config.model_variant}
            onChange={(e) => g.setConfig((c) => ({ ...c, model_variant: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2"
          >
            {MODEL_VARIANTS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="flex gap-2">
          <button onClick={() => g.checkModel()} className="flex-1 rounded-xl px-4 py-2 font-medium border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Check</button>
          <button onClick={() => g.startModelDownload()} className="flex-1 rounded-xl px-4 py-2 font-medium bg-indigo-500 text-white hover:bg-indigo-600">Download</button>
        </div>

        {g.modelDl.inProgress && (
          <div>
            <div className="flex justify-between text-xs">
              <span className="text-zinc-500">Downloading {g.modelDl.variant}</span>
              <span className="font-medium">{Math.floor(g.modelDl.percent)}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, Math.floor(g.modelDl.percent))}%` }}
                transition={{ type: "spring", stiffness: 120, damping: 20 }}
                className="h-full bg-gradient-to-r from-indigo-400 to-fuchsia-600"
              />
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

function LogsCard() {
  const g = useGlobal();
  return (
    <Card
      title="Logs"
      actions={<button onClick={() => g.appendLog("User added marker")} className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Add Marker</button>}
    >
      <div className="h-44 overflow-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-black/80 text-zinc-100 p-3 font-mono text-[12px]">
        {g.logs.map((l, i) => (
          <div key={i} className="opacity-90">{timeNow()} — {l}</div>
        ))}
      </div>
    </Card>
  );
}

// ------------------------------ Settings Modal ------------------------------
let _settingsModalOpen = false;
const listeners = new Set();
function openSettingsModal() { _settingsModalOpen = true; listeners.forEach((l) => l()); }
function closeSettingsModal() { _settingsModalOpen = false; listeners.forEach((l) => l()); }

function SettingsButton() {
  const [, setTick] = useState(0);
  useEffect(() => { const f = () => setTick((n) => n + 1); listeners.add(f); return () => listeners.delete(f); }, []);
  return (
    <button
      onClick={() => openSettingsModal()}
      className="px-3 py-1.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900"
    >
      Settings
    </button>
  );
}

function SettingsModalPortal() {
  const g = useGlobal();
  const [, setTick] = useState(0);
  useEffect(() => { const f = () => setTick((n) => n + 1); listeners.add(f); return () => listeners.delete(f); }, []);
  const open = _settingsModalOpen;
  const [tab, setTab] = useState("General");

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-3xl rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-100 dark:border-zinc-800">
          <h3 className="text-base font-semibold">Settings</h3>
          <button onClick={closeSettingsModal} className="rounded-xl px-3 py-1.5 text-sm border border-zinc-300 dark:border-zinc-700">Close</button>
        </div>

        <div className="px-5 py-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-1">
            <div className="flex md:flex-col gap-2">
              {['General','Process','Output','About'].map((t) => (
                <button key={t} onClick={() => setTab(t)} className={classNames(
                  "px-3 py-2 rounded-xl text-left border",
                  tab === t ? "border-amber-500 bg-amber-50 dark:bg-amber-950/40" : "border-zinc-200 dark:border-zinc-800"
                )}>{t}</button>
              ))}
            </div>
          </div>

          <div className="md:col-span-3">
            {tab === 'General' && <GeneralSettings />}
            {tab === 'Process' && <ProcessSettings />}
            {tab === 'Output' && <OutputSettings />}
            {tab === 'About' && <AboutPanel />}
          </div>
        </div>

        <div className="px-5 pb-5">
          <button
            onClick={() => { closeSettingsModal(); alert("Settings saved to settings.json via backend later."); }}
            className="w-full rounded-xl px-4 py-2 font-medium bg-emerald-500 text-white hover:bg-emerald-600"
          >
            Save
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function GeneralSettings() {
  const g = useGlobal();
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm text-zinc-500">Language</label>
        <select
          value={g.config.language}
          onChange={(e) => g.setConfig((c) => ({ ...c, language: e.target.value }))}
          className="mt-1 w-full rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2"
        >
          {LANGS.map((l) => (
            <option key={l} value={l}>{l === 'auto' ? 'auto-detect' : l}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <ToggleField
          label="Translate"
          checked={g.config.translate}
          onChange={(v) => g.setConfig((c) => ({ ...c, translate: v }))}
        />
        <div>
          <label className="text-sm text-zinc-500">Target language</label>
          <select
            disabled={!g.config.translate}
            value={g.config.target_language}
            onChange={(e) => g.setConfig((c) => ({ ...c, target_language: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2 disabled:opacity-50"
          >
            {LANGS.filter((l) => l !== 'auto').map((l) => (<option key={l} value={l}>{l}</option>))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <NumberField label="Chunk length (s)" value={g.config.chunk_length} onChange={(v) => g.setConfig((c) => ({ ...c, chunk_length: v }))} min={5} max={600} />
        <ToggleField label="Normalize" checked={g.config.normalize_audio} onChange={(v) => g.setConfig((c) => ({ ...c, normalize_audio: v }))} />
        <ToggleField label="Noise reduce" checked={g.config.reduce_noise} onChange={(v) => g.setConfig((c) => ({ ...c, reduce_noise: v }))} />
        <ToggleField label="Trim silence" checked={g.config.trim_silence} onChange={(v) => g.setConfig((c) => ({ ...c, trim_silence: v }))} />
      </div>
    </div>
  );
}

function ProcessSettings() {
  const g = useGlobal();
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm text-zinc-500">Model variant</label>
        <select
          value={g.config.model_variant}
          onChange={(e) => g.setConfig((c) => ({ ...c, model_variant: e.target.value }))}
          className="mt-1 w-full rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2"
        >
          {MODEL_VARIANTS.map((m) => (<option key={m} value={m}>{m}</option>))}
        </select>
      </div>

      <ToggleField
        label="Show system status"
        checked={g.config.show_system_status}
        onChange={(v) => g.setConfig((c) => ({ ...c, show_system_status: v }))}
      />
    </div>
  );
}

function OutputSettings() {
  const g = useGlobal();
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm text-zinc-500">Output format</label>
        <div className="mt-2 flex gap-2">
          {OUTPUT_FORMATS.map((fmt) => (
            <label key={fmt} className="flex items-center gap-2 rounded-xl border border-zinc-300 dark:border-zinc-700 px-3 py-2 cursor-pointer">
              <input
                type="radio"
                name="outfmt"
                checked={g.config.output_format === fmt}
                onChange={() => g.setConfig((c) => ({ ...c, output_format: fmt }))}
              />
              <span className="capitalize">{fmt}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="text-sm text-zinc-500">Output directory</label>
        <div className="mt-1 flex gap-2">
          <input
            type="text"
            value={g.config.output_directory}
            onChange={(e) => g.setConfig((c) => ({ ...c, output_directory: e.target.value }))}
            className="flex-1 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent px-3 py-2"
          />
          <button onClick={() => alert("Folder picker via backend later")}
            className="rounded-xl px-4 py-2 font-medium border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-900">Browse</button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <label className="text-sm">Delete temp files</label>
        <input type="checkbox" checked={g.config.delete_temp_files} onChange={(e) => g.setConfig((c) => ({ ...c, delete_temp_files: e.target.checked }))} />
      </div>
    </div>
  );
}

function AboutPanel() {
  return (
    <div className="space-y-3 text-sm text-zinc-600 dark:text-zinc-300">
      <p><strong>TranscribeMonkey</strong> is a Python 3.7+ toolkit that downloads, transcribes, and optionally translates audio. This UI is a Node.js/React prototype. No backend is wired yet.</p>
      <ul className="list-disc pl-5">
        <li>yt-dlp + FFmpeg for downloads and audio prep</li>
        <li>OpenAI Whisper + Torch for transcription</li>
        <li>googletrans / deep-translator for translation</li>
      </ul>
      <p>Logs to <code>app.log</code>. Settings persist in <code>src/settings/settings.json</code> in the real app.</p>
    </div>
  );
}

// ------------------------------ Small UI Parts ------------------------------
function TabBtn({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={classNames(
        "px-3 py-1.5 text-sm rounded-lg",
        active ? "bg-white dark:bg-zinc-900 shadow border border-zinc-200 dark:border-zinc-700" : "opacity-70 hover:opacity-100"
      )}
    >
      {children}
    </button>
  );
}

function ToggleField({ label, checked, onChange }) {
  return (
    <label className="flex items-center justify-between rounded-xl border border-zinc-200 dark:border-zinc-800 px-3 py-2">
      <span className="text-sm">{label}</span>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
    </label>
  );
}

function NumberField({ label, value, onChange, min = 0, max = 999 }) {
  return (
    <label className="rounded-xl border border-zinc-200 dark:border-zinc-800 px-3 py-2">
      <div className="text-sm text-zinc-500">{label}</div>
      <input
        type="number"
        className="mt-1 w-full bg-transparent focus:outline-none"
        value={value}
        min={min}
        max={max}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

function Footer() {
  return (
    <footer className="mx-auto max-w-6xl px-4 pb-8 text-xs text-zinc-500">
      <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800 mt-8">
        UI prototype only · No backend calls. © {new Date().getFullYear()} TranscribeMonkey
      </div>
    </footer>
  );
}

// ------------------------------ Utils & Mock Output ------------------------------
function timeNow() {
  const d = new Date();
  return d.toTimeString().slice(0, 8);
}

function estimateETA(percent) {
  const p = Math.max(1, percent);
  const remaining = (100 - p) * 0.6; // mock seconds
  const m = Math.floor(remaining / 60).toString().padStart(2, "0");
  const s = Math.floor(remaining % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function placeholderOutput(kind) {
  if (kind === "txt") return "Output will appear here once complete.";
  if (kind === "vtt") return "WEBVTT\n\n00:00:00.000 --> 00:00:03.000\n[Preview] Output will appear here.";
  return "1\n00:00:00,000 --> 00:00:03,000\n[Preview] Output will appear here.";
}

function makeMockSRT() {
  return `1\n00:00:00,000 --> 00:00:03,000\nHello and welcome to TranscribeMonkey.\n\n2\n00:00:03,000 --> 00:00:06,000\nThis is a mock transcript used for UI preview.\n\n3\n00:00:06,000 --> 00:00:09,000\nWhen wired to the backend, real results will show here.`;
}

function toVTT(srt) {
  // simple transform
  return (
    "WEBVTT\n\n" +
    srt
      .replaceAll(",", ".")
      .replace(/^(\d+)$/gm, "")
      .replace(/\n{3,}/g, "\n\n")
  );
}

function stripSRT(srt) {
  return srt
    .replace(/^(\d+)$/gm, "")
    .replace(/\d{2}:\d{2}:\d{2}[,.]\d{3} --> \d{2}:\d{2}:\d{2}[,.]\d{3}/g, "")
    .replace(/\n{2,}/g, "\n")
    .trim();
}
