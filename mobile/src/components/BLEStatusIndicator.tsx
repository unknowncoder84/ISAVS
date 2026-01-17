/**
 * BLE Status Indicator Component
 * Displays real-time BLE proximity status with RSSI and distance
 */
import React from 'react';
import {View, Text, StyleSheet, ActivityIndicator} from 'react-native';
import {SensorStatus} from '../types';

interface BLEStatusIndicatorProps {
  status: SensorStatus;
  rssi: number | null;
  distance: number | null;
  threshold: number;
  beaconName?: string;
}

export const BLEStatusIndicator: React.FC<BLEStatusIndicatorProps> = ({
  status,
  rssi,
  distance,
  threshold,
  beaconName = 'Classroom',
}) => {
  const getStatusColor = (): string => {
    switch (status) {
      case SensorStatus.READY:
        return '#10B981'; // Green
      case SensorStatus.SEARCHING:
        return '#F59E0B'; // Yellow
      case SensorStatus.FAILED:
        return '#EF4444'; // Red
      case SensorStatus.UNAVAILABLE:
        return '#6B7280'; // Gray
      default:
        return '#9CA3AF'; // Light gray
    }
  };

  const getStatusText = (): string => {
    switch (status) {
      case SensorStatus.READY:
        return `${beaconName} Detected ✓`;
      case SensorStatus.SEARCHING:
        return 'Searching for Classroom Signal...';
      case SensorStatus.FAILED:
        return 'Beacon Not Found';
      case SensorStatus.UNAVAILABLE:
        return 'Bluetooth Unavailable';
      default:
        return 'Initializing...';
    }
  };

  const getProximityMessage = (): string => {
    if (!rssi || !distance) return '';

    if (rssi > threshold) {
      return `In range (${distance.toFixed(1)}m)`;
    } else {
      return `Too far (${distance.toFixed(1)}m) - Move closer`;
    }
  };

  const isInRange = rssi !== null && rssi > threshold;

  return (
    <View style={[styles.container, {borderColor: getStatusColor()}]}>
      <View style={styles.header}>
        <View style={[styles.statusDot, {backgroundColor: getStatusColor()}]} />
        <Text style={styles.statusText}>{getStatusText()}</Text>
        {status === SensorStatus.SEARCHING && (
          <ActivityIndicator size="small" color={getStatusColor()} style={styles.spinner} />
        )}
      </View>

      {rssi !== null && (
        <View style={styles.details}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Signal Strength:</Text>
            <Text style={[styles.detailValue, {color: isInRange ? '#10B981' : '#EF4444'}]}>
              {rssi.toFixed(1)} dBm
            </Text>
          </View>

          {distance !== null && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Distance:</Text>
              <Text style={[styles.detailValue, {color: isInRange ? '#10B981' : '#EF4444'}]}>
                {distance.toFixed(1)} m
              </Text>
            </View>
          )}

          <Text style={[styles.proximityMessage, {color: isInRange ? '#10B981' : '#F59E0B'}]}>
            {getProximityMessage()}
          </Text>
        </View>
      )}

      {status === SensorStatus.UNAVAILABLE && (
        <Text style={styles.errorMessage}>
          Please enable Bluetooth in your device settings
        </Text>
      )}

      {status === SensorStatus.FAILED && (
        <Text style={styles.errorMessage}>
          Ensure faculty has started the session and you are in the classroom
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 2,
    padding: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  spinner: {
    marginLeft: 8,
  },
  details: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  proximityMessage: {
    fontSize: 14,
    fontWeight: '500',
    marginTop: 8,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

export default BLEStatusIndicator;
