import { Summary } from "@/types/dashboard";

type Props = {
  summary: Summary;
};

const cards = (summary: Summary) => [
  {
    title: "Total de Ilhas",
    value: summary.totalIlhas,
    subtitle: "Estacoes cadastradas",
  },
  {
    title: "Ilhas Ativas",
    value: summary.ilhasAtivas,
    subtitle: "Editando agora",
  },
  {
    title: "Tempo Medio",
    value: `${summary.tempoMedioMin}min`,
    subtitle: "Por sessao",
  },
  {
    title: "Concluidos Hoje",
    value: summary.concluidosHoje,
    subtitle: "Projetos finalizados",
  },
];

export default function SummaryCards({ summary }: Props) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards(summary).map((card) => (
        <div
          key={card.title}
          className="
            rounded-2xl border p-4 shadow-lg transition sm:p-5
            border-[rgba(0,0,0,0.08)] dark:border-white/10
            bg-[rgba(255,255,255,1)] dark:bg-[#020617]
          "
        >
          <p className="text-xs text-[rgba(120,120,120,1)] sm:text-sm">
            {card.title}
          </p>

          <h2 className="mt-2 text-3xl font-bold text-[rgba(30,30,30,1)] dark:text-[rgba(227,227,233,1)] sm:mt-3 sm:text-4xl">
            {card.value}
          </h2>

          <p className="mt-2 text-xs text-[rgba(140,140,140,1)] sm:text-sm">
            {card.subtitle}
          </p>
        </div>
      ))}
    </section>
  );
}
