'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, LineData, UTCTimestamp } from 'lightweight-charts';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface PortfolioDataPoint {
  time: string; // ISO date string
  value: number;
}

interface PortfolioChartProps {
  data?: PortfolioDataPoint[];
  isLoading?: boolean;
}

type TimePeriod = '7D' | '1M' | '3M' | '1Y' | 'ALL';

export function PortfolioChart({ data = [], isLoading = false }: PortfolioChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('1M');

  // Filter data based on selected time period
  const getFilteredData = (period: TimePeriod): PortfolioDataPoint[] => {
    if (!data || data.length === 0) return [];

    const now = new Date();
    let startDate = new Date();

    switch (period) {
      case '7D':
        startDate.setDate(now.getDate() - 7);
        break;
      case '1M':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case '3M':
        startDate.setMonth(now.getMonth() - 3);
        break;
      case '1Y':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'ALL':
        return data;
    }

    return data.filter(point => new Date(point.time) >= startDate);
  };

  // Convert data to chart format
  const convertToChartData = (dataPoints: PortfolioDataPoint[]): LineData[] => {
    return dataPoints.map(point => ({
      time: (new Date(point.time).getTime() / 1000) as UTCTimestamp,
      value: point.value,
    }));
  };

  // Initialize and update chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart if it doesn't exist
    if (!chartRef.current) {
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { color: 'transparent' },
          textColor: '#71717A',
        },
        grid: {
          vertLines: { color: '#F4F4F5' },
          horzLines: { color: '#F4F4F5' },
        },
        width: chartContainerRef.current.clientWidth,
        height: 300,
        rightPriceScale: {
          borderColor: '#E4E4E7',
        },
        timeScale: {
          borderColor: '#E4E4E7',
          timeVisible: true,
          secondsVisible: false,
        },
        crosshair: {
          mode: 1, // Magnet mode
          vertLine: {
            color: '#3B82F6',
            width: 1,
            style: 3, // Dashed
            labelBackgroundColor: '#3B82F6',
          },
          horzLine: {
            color: '#3B82F6',
            width: 1,
            style: 3,
            labelBackgroundColor: '#3B82F6',
          },
        },
      });

      chartRef.current = chart;

      // Create area series
      const areaSeries = chart.addAreaSeries({
        lineColor: '#3B82F6',
        topColor: 'rgba(59, 130, 246, 0.3)',
        bottomColor: 'rgba(59, 130, 246, 0.05)',
        lineWidth: 2,
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      });

      seriesRef.current = areaSeries;

      // Handle resize
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
          seriesRef.current = null;
        }
      };
    }
  }, []);

  // Update chart data when data or period changes
  useEffect(() => {
    if (!seriesRef.current || !data || data.length === 0) return;

    const filteredData = getFilteredData(selectedPeriod);
    const chartData = convertToChartData(filteredData);

    if (chartData.length > 0) {
      seriesRef.current.setData(chartData);
      
      // Fit content to view
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }
    }
  }, [data, selectedPeriod]);

  const handlePeriodChange = (period: TimePeriod) => {
    setSelectedPeriod(period);
  };

  const periods: TimePeriod[] = ['7D', '1M', '3M', '1Y', 'ALL'];

  // Generate mock data if no real data (for demo purposes)
  const hasMockData = data.length === 0 && !isLoading;

  return (
    <div className="space-y-4">
      {/* Time Period Selector */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          {periods.map(period => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'default' : 'outline'}
              size="sm"
              onClick={() => handlePeriodChange(period)}
              className="px-3 py-1 h-8 text-xs"
            >
              {period}
            </Button>
          ))}
        </div>
        
        {data.length > 0 && (
          <div className="text-sm text-muted-foreground">
            {data.length} data points
          </div>
        )}
      </div>

      {/* Chart Container */}
      <div className="relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-10 rounded-lg">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">Loading chart data...</p>
            </div>
          </div>
        )}
        
        {!isLoading && data.length === 0 && (
          <div className="h-[300px] flex items-center justify-center bg-muted/10 rounded-lg border-2 border-dashed">
            <div className="text-center text-muted-foreground px-4">
              <svg
                className="h-12 w-12 mx-auto mb-2 opacity-50"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
              <p className="text-sm font-medium">No investment data yet</p>
              <p className="text-xs mt-1">Make your first deposit to see your portfolio growth</p>
            </div>
          </div>
        )}

        {!isLoading && data.length > 0 && (
          <div
            ref={chartContainerRef}
            className="rounded-lg border bg-white overflow-hidden"
            style={{ minHeight: '300px' }}
          />
        )}
      </div>

      {/* Chart Legend/Stats */}
      {data.length > 0 && !isLoading && (
        <div className="grid grid-cols-3 gap-4 pt-2 border-t">
          <div>
            <p className="text-xs text-muted-foreground">Starting Balance</p>
            <p className="text-sm font-semibold">
              ${data[0]?.value.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Current Balance</p>
            <p className="text-sm font-semibold">
              ${data[data.length - 1]?.value.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Growth</p>
            <p className={`text-sm font-semibold ${
              data[data.length - 1]?.value >= data[0]?.value 
                ? 'text-green-600' 
                : 'text-red-600'
            }`}>
              {data[0]?.value > 0
                ? `${(((data[data.length - 1]?.value - data[0]?.value) / data[0]?.value) * 100).toFixed(2)}%`
                : '0.00%'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
