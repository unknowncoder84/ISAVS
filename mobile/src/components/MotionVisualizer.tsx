/**
 * Motion Visualizer Component (Debug Mode)
 * Real-time visualization of accelerometer and gyroscope data
 */
import React, {useEffect, useRef} from 'react';
import {View, Text, StyleSheet, ScrollView, Dimensions} from 'react';
import {AccelerometerData, GyroscopeData} from '../types';

interface MotionVisualizerProps {
  accelerometerData: AccelerometerData[];
  gyroscopeData: GyroscopeData[];
  samplingRate: number;
  nodDetected: boolean;
  shakeDetected: boolean;
}

const SCREEN_WIDTH = Dimensions.get('window').width - 32;
const GRAPH_HEIGHT = 120;
const MAX_SAMPLES = 50; // Show last 50 samples

export const MotionVisualizer: React.FC<MotionVisualizerProps> = ({
  accelerometerData,
  gyroscopeData,
  samplingRate,
  nodDetected,
  shakeDetected,
}) => {
  /**
   * Render accelerometer graph
   */
  const renderAccelerometerGraph = () => {
    const recentData = accelerometerData.slice(-MAX_SAMPLES);
    if (recentData.length === 0) return null;

    // Find min/max for scaling
    const allValues = recentData.flatMap(d => [d.x, d.y, d.z]);
    const min = Math.min(...allValues, -2);
    const max = Math.max(...allValues, 2);
    const range = max - min || 1;

    const scaleY = (value: number) => {
      return GRAPH_HEIGHT - ((value - min) / range) * GRAPH_HEIGHT;
    };

    const stepX = SCREEN_WIDTH / MAX_SAMPLES;

    return (
      <View style={styles.graphContainer}>
        <Text style={styles.graphTitle}>Accelerometer (m/s²)</Text>
        <View style={styles.graph}>
          {/* Grid lines */}
          <View style={[styles.gridLine, {top: 0}]} />
          <View style={[styles.gridLine, {top: GRAPH_HEIGHT / 2}]} />
          <View style={[styles.gridLine, {top: GRAPH_HEIGHT}]} />

          {/* X-axis (red) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`x-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.x),
                    backgroundColor: '#EF4444',
                  },
                ]}
              />
            ))}
          </View>

          {/* Y-axis (green) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`y-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.y),
                    backgroundColor: '#10B981',
                  },
                ]}
              />
            ))}
          </View>

          {/* Z-axis (blue) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`z-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.z),
                    backgroundColor: '#3B82F6',
                  },
                ]}
              />
            ))}
          </View>
        </View>

        {/* Legend */}
        <View style={styles.legend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#EF4444'}]} />
            <Text style={styles.legendText}>X</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#10B981'}]} />
            <Text style={styles.legendText}>Y</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#3B82F6'}]} />
            <Text style={styles.legendText}>Z</Text>
          </View>
        </View>
      </View>
    );
  };

  /**
   * Render gyroscope graph
   */
  const renderGyroscopeGraph = () => {
    const recentData = gyroscopeData.slice(-MAX_SAMPLES);
    if (recentData.length === 0) return null;

    // Find min/max for scaling
    const allValues = recentData.flatMap(d => [d.x, d.y, d.z]);
    const min = Math.min(...allValues, -1);
    const max = Math.max(...allValues, 1);
    const range = max - min || 1;

    const scaleY = (value: number) => {
      return GRAPH_HEIGHT - ((value - min) / range) * GRAPH_HEIGHT;
    };

    const stepX = SCREEN_WIDTH / MAX_SAMPLES;

    return (
      <View style={styles.graphContainer}>
        <Text style={styles.graphTitle}>Gyroscope (rad/s)</Text>
        <View style={styles.graph}>
          {/* Grid lines */}
          <View style={[styles.gridLine, {top: 0}]} />
          <View style={[styles.gridLine, {top: GRAPH_HEIGHT / 2}]} />
          <View style={[styles.gridLine, {top: GRAPH_HEIGHT}]} />

          {/* X-axis (red) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`x-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.x),
                    backgroundColor: '#EF4444',
                  },
                ]}
              />
            ))}
          </View>

          {/* Y-axis (green) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`y-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.y),
                    backgroundColor: '#10B981',
                  },
                ]}
              />
            ))}
          </View>

          {/* Z-axis (blue) */}
          <View style={styles.linePath}>
            {recentData.map((data, index) => (
              <View
                key={`z-${index}`}
                style={[
                  styles.dataPoint,
                  {
                    left: index * stepX,
                    top: scaleY(data.z),
                    backgroundColor: '#3B82F6',
                  },
                ]}
              />
            ))}
          </View>
        </View>

        {/* Legend */}
        <View style={styles.legend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#EF4444'}]} />
            <Text style={styles.legendText}>X</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#10B981'}]} />
            <Text style={styles.legendText}>Y</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, {backgroundColor: '#3B82F6'}]} />
            <Text style={styles.legendText}>Z</Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Motion Data Visualizer (Debug)</Text>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Sampling Rate</Text>
            <Text style={styles.statValue}>{samplingRate.toFixed(1)} Hz</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Accel Samples</Text>
            <Text style={styles.statValue}>{accelerometerData.length}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Gyro Samples</Text>
            <Text style={styles.statValue}>{gyroscopeData.length}</Text>
          </View>
        </View>

        {/* Motion Detection Status */}
        <View style={styles.detectionContainer}>
          <View style={[styles.detectionBadge, nodDetected && styles.detectionActive]}>
            <Text style={[styles.detectionText, nodDetected && styles.detectionTextActive]}>
              {nodDetected ? '✓' : '○'} Nod
            </Text>
          </View>
          <View style={[styles.detectionBadge, shakeDetected && styles.detectionActive]}>
            <Text style={[styles.detectionText, shakeDetected && styles.detectionTextActive]}>
              {shakeDetected ? '✓' : '○'} Shake
            </Text>
          </View>
        </View>

        {/* Graphs */}
        {renderAccelerometerGraph()}
        {renderGyroscopeGraph()}

        {/* Latest Values */}
        {accelerometerData.length > 0 && (
          <View style={styles.valuesContainer}>
            <Text style={styles.valuesTitle}>Latest Accelerometer</Text>
            <Text style={styles.valuesText}>
              X: {accelerometerData[accelerometerData.length - 1].x.toFixed(3)} m/s²
            </Text>
            <Text style={styles.valuesText}>
              Y: {accelerometerData[accelerometerData.length - 1].y.toFixed(3)} m/s²
            </Text>
            <Text style={styles.valuesText}>
              Z: {accelerometerData[accelerometerData.length - 1].z.toFixed(3)} m/s²
            </Text>
          </View>
        )}

        {gyroscopeData.length > 0 && (
          <View style={styles.valuesContainer}>
            <Text style={styles.valuesTitle}>Latest Gyroscope</Text>
            <Text style={styles.valuesText}>
              X: {gyroscopeData[gyroscopeData.length - 1].x.toFixed(3)} rad/s
            </Text>
            <Text style={styles.valuesText}>
              Y: {gyroscopeData[gyroscopeData.length - 1].y.toFixed(3)} rad/s
            </Text>
            <Text style={styles.valuesText}>
              Z: {gyroscopeData[gyroscopeData.length - 1].z.toFixed(3)} rad/s
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statItem: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 12,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 11,
    color: '#6B7280',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  detectionContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 12,
  },
  detectionBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    backgroundColor: '#FFFFFF',
  },
  detectionActive: {
    borderColor: '#10B981',
    backgroundColor: '#D1FAE5',
  },
  detectionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  detectionTextActive: {
    color: '#10B981',
  },
  graphContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  graphTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  graph: {
    width: SCREEN_WIDTH,
    height: GRAPH_HEIGHT,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    position: 'relative',
  },
  gridLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: '#E5E7EB',
  },
  linePath: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  dataPoint: {
    position: 'absolute',
    width: 3,
    height: 3,
    borderRadius: 1.5,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 12,
    gap: 16,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6,
  },
  legendText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '600',
  },
  valuesContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  valuesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  valuesText: {
    fontSize: 13,
    color: '#6B7280',
    fontFamily: 'monospace',
    marginBottom: 4,
  },
});

export default MotionVisualizer;
