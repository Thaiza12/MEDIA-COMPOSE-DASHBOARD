import { Ilha } from "@/types/dashboard";

function getStatusColor(status: string) {
  switch (status) {
    case "Pronto para editar":
      return "bg-emerald-500/20 text-emerald-300 border-emerald-500/20";

    case "Editando":
      return "bg-yellow-500/20 text-yellow-300 border-yellow-500/20";

    case "Editado":
      return "bg-blue-500/20 text-blue-300 border-blue-500/20";

    case "Gaveta":
      return "bg-purple-500/20 text-purple-300 border-purple-500/20";

    case "Exibido":
      return "bg-cyan-500/20 text-cyan-300 border-cyan-500/20";

    case "Exportado":
      return "bg-orange-500/20 text-orange-300 border-orange-500/20";

    case "Home Office":
      return "bg-pink-500/20 text-pink-300 border-pink-500/20";

    case "Fora do Turno":
      return "bg-slate-500/20 text-slate-300 border-slate-500/20";

    default:
      return "bg-slate-500/20 text-slate-300 border-slate-500/20";
  }
}

type Props = {
  ilha: Ilha;
};

export default function EditorCard({ ilha }: Props) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-lg shadow-black/20 transition hover:border-cyan-500/30">

      <div className="flex items-start justify-between gap-3">

        <div className="flex items-center gap-3">

          <div className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-slate-800 text-sm font-bold text-white">
            {ilha.avatar}

            <span
              className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-slate-950 ${
                ilha.status === "Editando"
                  ? "bg-yellow-400"
                  : ilha.status === "Pronto para editar"
                  ? "bg-emerald-400"
                  : ilha.status === "Exportado"
                  ? "bg-orange-400"
                  : "bg-slate-400"
              }`}
            />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">
              {ilha.editor}
            </h3>

            <p className="text-sm text-slate-400">
              {ilha.ilha} • {ilha.regional}
            </p>
          </div>
        </div>

        <span
          className={`rounded-full border px-3 py-1 text-xs font-medium ${getStatusColor(
            ilha.status
          )}`}
        >
          {ilha.status}
        </span>
      </div>

      <div className="mt-5 rounded-xl bg-slate-900/70 p-4">

        <p className="text-xs uppercase tracking-wide text-slate-500">
          Projeto Atual
        </p>

        <p className="mt-2 text-sm font-semibold text-white">
          {ilha.projeto}
        </p>

      </div>

      <div className="mt-5">

        <div className="mb-2 flex items-center justify-between text-sm">

          <span className="text-slate-400">
            Progresso
          </span>

          <span className="font-medium text-white">
            {ilha.progresso}%
          </span>

        </div>

        <div className="h-2 w-full rounded-full bg-slate-800">

          <div
            className="h-2 rounded-full bg-cyan-400 transition-all duration-500"
            style={{ width: `${ilha.progresso}%` }}
          />

        </div>

      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">

        <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3">
          <p className="text-slate-500">
            Início
          </p>

          <p className="mt-1 font-medium text-white">
            {ilha.inicio}
          </p>
        </div>

        <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3">
          <p className="text-slate-500">
            Arquivo
          </p>

          <p className="mt-1 font-medium text-white">
            {ilha.arquivoGb} GB
          </p>
        </div>

      </div>

      <div className="mt-5 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">

        <p className="text-sm text-cyan-300">
          Previsão IA
        </p>

        <p className="mt-1 text-sm font-semibold text-white">
          {ilha.previsaoRestanteMin}min restantes
        </p>

        <p className="text-xs text-slate-400">
          Final previsto: {ilha.previsaoFim}
        </p>

      </div>

    </div>
  );
}