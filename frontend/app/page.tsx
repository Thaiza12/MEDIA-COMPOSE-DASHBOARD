"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import SummaryCards from "@/components/SummaryCards";
import TabsNav from "@/components/TabsNav";
import EditorsGrid from "@/components/EditorsGrid";
import AIPanel from "@/components/AIPanel";
import ChartsSection from "@/components/ChartsSection";
import FilterBar from "@/components/FilterBar";
import { DashboardData, ViewMode } from "@/types/dashboard";

export default function HomePage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState(0);

  const [search, setSearch] = useState("");
  const [editorFilter, setEditorFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [retrancaFilter, setRetrancaFilter] = useState("");

  // futuramente virá do login/backend
  const [viewMode] = useState<ViewMode>("gerente");

  async function fetchDashboard(showLoading = false) {
    try {
      if (showLoading) setLoading(true);
      setError(null);

      const response = await fetch("http://127.0.0.1:5000/dashboard", {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Erro ao buscar dados do dashboard.");
      }

      const result: DashboardData = await response.json();
      setData(result);
    } catch (err) {
      setError("Não foi possível carregar os dados do backend.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // primeira carga com tela de loading
    fetchDashboard(true);

    // polling silencioso a cada 3s
    const interval = setInterval(() => {
      fetchDashboard(false);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white px-4 py-6 dark:bg-black md:px-6 2xl:px-8">
        <p className="text-lg text-white">
          Carregando dados do backend...
        </p>
      </main>
    );
  }

  if (error && !data) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-white px-4 py-6 dark:bg-black md:px-6 2xl:px-8">
        <p className="text-lg text-red-400">
          {error}
        </p>

        <button
          onClick={() => fetchDashboard(true)}
          className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/90 dark:bg-slate-900/70 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 shadow-sm backdrop-blur transition-all duration-200 hover:bg-slate-50 hover:text-slate-900 dark:hover:bg-slate-800/80 dark:hover:text-white"
        >
          Tentar novamente
        </button>
      </main>
    );
  }

  if (!data) return null;

  const isPublicView = viewMode === "publico";
  const isTeamView = viewMode === "gestor";

  const baseIlhas = isTeamView
    ? data.ilhas.filter((ilha) =>
        ["ILHA-01", "ILHA-02"].includes(ilha.ilha)
      )
    : data.ilhas;

  const ilhasFiltradas = baseIlhas.filter((ilha) => {
    const matchSearch = ilha.projeto
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchEditor = editorFilter
      ? ilha.editor === editorFilter
      : true;

    const matchStatus = statusFilter
      ? ilha.status === statusFilter
      : true;

    const retrancaCompleta = `${ilha.programa} - ${ilha.retranca}`;

    const matchRetranca = retrancaFilter
      ? retrancaCompleta === retrancaFilter
      : true;

    return matchSearch && matchEditor && matchStatus && matchRetranca;
  });

  const ilhasPublicas = ilhasFiltradas.map((ilha, index) => ({
    ...ilha,
    editor: `Editor ${index + 1}`,
    avatar: "?",
    previsaoRestanteMin: 0,
    previsaoFim: "--:--",
  }));

  const ilhasVisiveis = isPublicView ? ilhasPublicas : ilhasFiltradas;

  const showIlhas = activeTab === 0 || activeTab === 1;
  const showCharts = activeTab === 0 || activeTab === 2;

  return (
    <main className="min-h-screen bg-white px-4 py-6 dark:bg-black md:px-6 2xl:px-8">

      <div className="mx-auto flex w-full max-w-full flex-col gap-6 2xl:gap-7">

        <Header
          atualizadoEm={data.atualizadoEm}
          statusSistema={data.statusSistema}
          onRefresh={() => fetchDashboard(false)}
        />

        <SummaryCards summary={data.summary} />

        <TabsNav
          active={activeTab}
          onChange={setActiveTab}
        />

        {showIlhas && (
          <FilterBar
            ilhas={baseIlhas}
            search={search}
            onSearch={setSearch}

            editorFilter={editorFilter}
            onEditorFilter={setEditorFilter}

            statusFilter={statusFilter}
            onStatusFilter={setStatusFilter}

            retrancaFilter={retrancaFilter}
            onRetrancaFilter={setRetrancaFilter}
          />
        )}

        {showIlhas && (
          <section
            className={`grid gap-6 ${
              isPublicView
                ? "xl:grid-cols-1"
                : "xl:grid-cols-[5fr_1.2fr]"
            }`}
          >
            <EditorsGrid ilhas={ilhasVisiveis} />

            {!isPublicView && (
              <div className="sticky top-4 h-fit">
                <AIPanel ia={data.ia} />
              </div>
            )}
          </section>
        )}

        {showCharts && (
          <ChartsSection
            horasPorDia={data.horasPorDia}
            atividadePorHora={data.atividadePorHora}
          />
        )}

        {activeTab === 3 && (
          <div className="rounded-2xl border border-white/10 bg-slate-950 p-8 text-center text-slate-400">
            Histórico em desenvolvimento
          </div>
        )}

      </div>
    </main>
  );
}