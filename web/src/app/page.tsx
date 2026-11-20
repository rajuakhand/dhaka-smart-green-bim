export default function LandingPage() {
  return (
    <div className="min-h-[calc(100vh-200px)]">
      <section className="py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
          DhakaSmart
        </h1>
        <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto mb-8">
          Bangladesh Climate-Aware Building Performance &amp; Space Optimization Platform
        </p>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-12">
          Evidence-driven building analysis for Dhaka&apos;s dense urban environment.
          Deterministic calculations, traceable sources, and verified engineering rules.
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/projects/new"
            className="px-8 py-4 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
          >
            Start New Project
          </a>
          <a
            href="/dashboard"
            className="px-8 py-4 bg-white text-slate-900 border border-slate-300 rounded-lg font-semibold hover:bg-slate-50 transition-colors"
          >
            View Dashboard
          </a>
        </div>
      </section>

      <section className="py-16 bg-white rounded-2xl border border-slate-200">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">
          Platform Modules
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 px-8 pb-8">
          {[
            { icon: "🏗️", title: "Building Setup", desc: "Project metadata, geometry, orientation, materials" },
            { icon: "📏", title: "Room Analyzer", desc: "Per-room geometry, occupancy, area per person" },
            { icon: "💨", title: "Ventilation Screening", desc: "Opening ratio, cross-ventilation potential" },
            { icon: "☀️", title: "Daylight Screening", desc: "Glazing ratio, obstruction, shading assessment" },
            { icon: "⚡", title: "Energy Estimator", desc: "Preliminary cooling, lighting, equipment energy" },
            { icon: "🌱", title: "Carbon Calculator", desc: "Operational electricity emissions with traceable factors" },
            { icon: "📐", title: "Density & Urban Context", desc: "FAR, ground coverage, open space, RAJUK DAP" },
            { icon: "🏛️", title: "Structural Screening", desc: "Missing info flags, professional review reminders" },
            { icon: "📊", title: "Design Optimization", desc: "Baseline vs alternative comparison" },
          ].map((module, i) => (
            <div key={i} className="p-6 border border-slate-200 rounded-lg hover:border-emerald-400 transition-colors">
              <span className="text-3xl">{module.icon}</span>
              <h3 className="font-semibold text-lg mt-3 mb-2">{module.title}</h3>
              <p className="text-slate-600 text-sm">{module.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">
          Engineering Principles
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            "No fabricated data — every rule has a traceable source",
            "Deterministic calculations — testable and documented",
            "AI assists, never replaces engineering calculation logic",
            "Uncertainty always shown — every result carries confidence",
            "Preliminary = preliminary — no pass/fail without simulation",
            "Professional review required — structural safety needs qualified engineer",
          ].map((principle, i) => (
            <div key={i} className="p-6 bg-slate-100 rounded-lg">
              <span className="text-emerald-600 font-bold text-xl">{i + 1}.</span>
              <p className="mt-2 text-slate-700">{principle}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16 text-center">
        <h2 className="text-3xl font-bold text-slate-900 mb-6">
          Verified Data Sources
        </h2>
        <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
          {[
            "BNBC 2020",
            "RAJUK DAP 2022-2035",
            "DoE Grid Emission Factor",
            "Ember / OWID",
            "EnergyPlus EPW",
            "NASA POWER",
            "SREDA BEEER",
            "World Bank BEEER Survey",
          ].map((source, i) => (
            <span
              key={i}
              className="px-4 py-2 bg-emerald-50 text-emerald-700 rounded-full text-sm font-medium border border-emerald-200"
            >
              ✓ {source}
            </span>
          ))}
        </div>
      </section>

      <section className="py-16 bg-amber-50 border border-amber-200 rounded-xl p-8">
        <h3 className="text-xl font-bold text-amber-900 mb-4">
          ⚠️ Preliminary Analysis Only
        </h3>
        <p className="text-amber-800">
          This platform provides screening-level analysis with documented assumptions and limitations.
          Results are NOT a substitute for verified structural assessment, certified energy simulation,
          professional engineering review, or regulatory compliance certification.
          Always engage qualified professionals for design decisions.
        </p>
      </section>
    </div>
  );
}