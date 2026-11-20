import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DhakaSmart | Urban Density & Green BIM",
  description: "Bangladesh Climate-Aware Building Performance & Space Optimization Platform",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold text-slate-900">
              <span className="text-emerald-600">🏢</span>
              <span>DhakaSmart</span>
            </a>
            <div className="hidden md:flex items-center gap-6 text-sm font-medium">
              <a href="/dashboard" className="hover:text-emerald-600 transition-colors">Dashboard</a>
              <a href="/phase2" className="hover:text-emerald-600 transition-colors">Phase 2</a>
              <a href="/projects/new" className="hover:text-emerald-600 transition-colors">New Project</a>
              <a href="/documentation" className="hover:text-emerald-600 transition-colors">Docs</a>
              <a href="https://github.com/rajuakhand/dhaka-smart-green-bim" target="_blank" className="hover:text-emerald-600 transition-colors">GitHub</a>
            </div>
            <div className="md:hidden">
              <button className="text-slate-600">☰</button>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
          <p>DhakaSmart Urban Density &amp; Green BIM — Preliminary Building Performance Analysis</p>
          <p className="mt-2">⚠️ All results are preliminary. Requires professional review for design decisions.</p>
        </footer>
      </body>
    </html>
  );
}