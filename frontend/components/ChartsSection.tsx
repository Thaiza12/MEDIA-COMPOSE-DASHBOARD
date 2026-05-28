"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";
import { ChartPoint } from "@/types/dashboard";

type Props = {
  horasPorDia: ChartPoint[];
  atividadePorHora: ChartPoint[];
};

export default function ChartsSection({
  horasPorDia,
  atividadePorHora,
}: Props) {
  return (
    <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">

      {/* LINE CHART */}
      <div className="
        min-w-0 overflow-hidden rounded-2xl border p-5
        border-[rgba(0,0,0,0.08)] dark:border-white/10
        bg-white dark:bg-[#020617]
      ">
        <h2 className="
          mb-4 text-lg font-semibold
          text-slate-900 dark:text-[rgba(227,227,233,1)]
        ">
          Horas Trabalhadas por Dia
        </h2>

        <div className="h-64 w-full min-w-0 sm:h-72 md:h-80">
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <LineChart data={horasPorDia}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(200,200,200,0.3)"
              />

              <XAxis
                dataKey="label"
                stroke="rgba(120,120,120,1)"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />

              <YAxis
                stroke="rgba(120,120,120,1)"
                tick={{ fontSize: 12 }}
                width={34}
              />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="valor"
                stroke="#38bdf8"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* BAR CHART */}
      <div className="
        min-w-0 overflow-hidden rounded-2xl border p-5
        border-[rgba(0,0,0,0.08)] dark:border-white/10
        bg-white dark:bg-[#020617]
      ">
        <h2 className="
          mb-4 text-lg font-semibold
          text-slate-900 dark:text-[rgba(227,227,233,1)]
        ">
          Atividade por Hora
        </h2>

        <div className="h-64 w-full min-w-0 sm:h-72 md:h-80">
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <BarChart data={atividadePorHora}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(200,200,200,0.3)"
              />

              <XAxis
                dataKey="label"
                stroke="rgba(120,120,120,1)"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />

              <YAxis
                stroke="rgba(120,120,120,1)"
                tick={{ fontSize: 12 }}
                width={34}
              />

              <Tooltip />

              <Bar
                dataKey="valor"
                fill="#22c55e"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
