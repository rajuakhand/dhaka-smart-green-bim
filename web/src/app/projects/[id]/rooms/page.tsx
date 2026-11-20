"use client";

import { useState } from "react";

const rooms = [
  { id: 1, name: "Living Room", type: "Residential", length: 5, width: 4, height: 3, occupants: 4, windowArea: 4, openableArea: 2 },
  { id: 2, name: "Bedroom 1", type: "Residential", length: 4, width: 3, height: 3, occupants: 2, windowArea: 3, openableArea: 1.5 },
  { id: 3, name: "Bedroom 2", type: "Residential", length: 4, width: 3, height: 3, occupants: 2, windowArea: 3, openableArea: 1.5 },
  { id: 4, name: "Kitchen", type: "Residential", length: 3, width: 3, height: 3, occupants: 2, windowArea: 2, openableArea: 1 },
  { id: 5, name: "Bathroom", type: "Residential", length: 2, width: 2, height: 3, occupants: 1, windowArea: 1, openableArea: 0.5 },
];

export default function RoomEditorPage() {
  const [selected, setSelected] = useState(1);
  const [roomData, setRoomData] = useState(rooms);

  const updateRoom = (id: number, field: string, value: any) => {
    setRoomData(roomData.map((r) => (r.id === id ? { ...r, [field]: value } : r)));
  };

  const current = roomData.find((r) => r.id === selected)!;
  const area = current.length * current.width;
  const volume = area * current.height;
  const areaPerPerson = area / current.occupants;
  const bnbcPass = areaPerPerson >= 9.3;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Room Editor</h1>
        <p className="text-slate-600 mt-2">Module B — Per-room geometry, occupancy, area per person</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold mb-4">Rooms ({roomData.length})</h2>
          <div className="space-y-2">
            {roomData.map((room) => (
              <button
                key={room.id}
                onClick={() => setSelected(room.id)}
                className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                  selected === room.id
                    ? "bg-emerald-50 border-emerald-300 text-emerald-900"
                    : "border-slate-200 hover:bg-slate-50"
                }`}
              >
                <span className="font-medium">{room.name}</span>
                <span className="block text-xs text-slate-500">{room.type} · {room.length}×{room.width}m</span>
              </button>
            ))}
          </div>
          <button className="w-full mt-4 px-4 py-2 border border-dashed border-slate-300 rounded-lg text-sm hover:bg-slate-50">
            + Add Room
          </button>
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 space-y-4">
          <h2 className="text-xl font-semibold">{current.name}</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Length (m)</label>
              <input type="number" step="0.1" value={current.length} onChange={(e) => updateRoom(selected, "length", parseFloat(e.target.value) || 0)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Width (m)</label>
              <input type="number" step="0.1" value={current.width} onChange={(e) => updateRoom(selected, "width", parseFloat(e.target.value) || 0)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Height (m)</label>
              <input type="number" step="0.1" value={current.height} onChange={(e) => updateRoom(selected, "height", parseFloat(e.target.value) || 0)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Occupants</label>
              <input type="number" value={current.occupants} onChange={(e) => updateRoom(selected, "occupants", parseInt(e.target.value) || 1)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Window Area (m²)</label>
              <input type="number" step="0.1" value={current.windowArea} onChange={(e) => updateRoom(selected, "windowArea", parseFloat(e.target.value) || 0)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Openable Area (m²)</label>
              <input type="number" step="0.1" value={current.openableArea} onChange={(e) => updateRoom(selected, "openableArea", parseFloat(e.target.value) || 0)} className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4 p-4 bg-slate-50 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900">{area.toFixed(1)}</div>
              <div className="text-xs text-slate-500">Floor Area (m²)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900">{volume.toFixed(1)}</div>
              <div className="text-xs text-slate-500">Volume (m³)</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${bnbcPass ? "text-emerald-600" : "text-red-600"}`}>{areaPerPerson.toFixed(1)}</div>
              <div className="text-xs text-slate-500">Area/Person (m²)</div>
            </div>
          </div>

          <div className={`p-4 rounded-lg text-sm ${bnbcPass ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"}`}>
            <p className="font-semibold">{bnbcPass ? "✅ BNBC Occupancy: Pass" : "⚠️ BNBC Occupancy: Review"}</p>
            <p className="mt-1">{areaPerPerson.toFixed(1)} m²/person (BNBC min: 9.3 m²/person)</p>
          </div>
        </div>
      </div>
    </div>
  );
}