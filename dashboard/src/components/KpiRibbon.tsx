import React from 'react';

interface KpiPanelProps {
  panelId: number;
}

const KpiPanel: React.FC<KpiPanelProps> = ({ panelId }) => {
  // Use Vite's environment variable syntax
  const grafanaUrl = import.meta.env.VITE_GRAFANA_URL;
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="border p-4">
        KPI Panel {panelId} - Grafana would be embedded here in production
      </div>
    </div>
  );
};

const KpiRibbon: React.FC = () => {
  console.log('KPI Ribbon component rendered');
  const panelIds = [1, 2, 3, 4]; // Replace with actual panel IDs

  return (
    <div className="flex flex-wrap justify-center gap-4 p-4 bg-gray-50 shadow-md rounded-lg mb-6">
      {panelIds.map(id => (
        <KpiPanel key={id} panelId={id} />
      ))}
    </div>
  );
};

export default KpiRibbon;
