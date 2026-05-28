import { Ilha } from "@/types/dashboard";
import EditorCard from "./EditorCard";

type Props = {
  ilhas: Ilha[];
};

export default function EditorsGrid({ ilhas }: Props) {
  return (
    <section className="min-w-0">

      <h2 className="mb-4 text-xl font-semibold text-white">
        Ilhas em Atividade
      </h2>

      {ilhas.length === 0 ? (
        <div className="rounded-2xl border border-white/10 bg-slate-950 p-8 text-center text-slate-400">
          Nenhuma ilha encontrada para os filtros selecionados.
        </div>
      ) : (
        <div
          className="
            grid
            gap-4
            grid-cols-1
            md:grid-cols-2
            xl:grid-cols-3
            2xl:grid-cols-4
          "
        >
          {ilhas.map((ilha) => (
            <EditorCard
              key={ilha.id}
              ilha={ilha}
            />
          ))}
        </div>
      )}

    </section>
  );
}