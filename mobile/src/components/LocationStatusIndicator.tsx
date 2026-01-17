/**
 * Location Status Indicator Component
 * Displays GPS and barometer status for location verification
 */
import React from 'react';
import {View, Text, StyleSheet, ActivityIndicator} from 'react';
import {SensorStatus, LocationData, PressureData} from '../types';

interface LocationStatusIndicatorProps {
  gpsStatus: SensorStatus;
  barometerStatus: SensorStatus;
  location: LocationData | null;
  pressure: PressureData | null;
  distanceFromClassroom?: number | null;
}

export const LocationStatusIndicator: React.FC<LocationStatusIndicatorProps> = ({
  gpsStatus,
  barometerStatus,
  location,
  pressure,
  distanceFromClassroom,
}) => {
  const getGPSStatusColor = (): string => {
    switch (gpsStatus) {
      case SensorStatus.READY:
        return '#10B981'; // Green
      case SensorStatus.SEARCHING:
        return '#F59E0B'; // Yellow
      case SensorStatus.FAILED:
      case SensorStatus.UNAVAILABLE:
        return '#EF4444'; // Red
      default:
        return '#9CA3AF'; // Gray
    }
  };

  const getBarometerStatusColor = (): string => {
    switch (barometerStatus) {
      case SensorStatus.READY:
        return '#10B981'; // Green
      case SensorStatus.SEARCHING:
        return '#F59E0B'; // Yellow
      case SensorStatus.FAILED:
      case SensorStatus.UNAVAILABLE:
        return '#6B7280'; // Gray (optional sensor)
      default:
        return '#9CA3AF'; // Gray
    }
  };

  const getGPSStatusText = (): string => {
    switch (gpsStatus) {
      case SensorStatus.READY:
        return 'Location Verified ✓';
      case SensorStatus.SEARCHING:
        return 'Acquiring GPS...';
      case SensorStatus.FAILED:
        return 'GPS Failed';
      case SensorStatus.UNAVAILABLE:
        return 'GPS Unavailable';
      default:
        return 'GPS Idle';
    }
  };

  const getBarometerStatusText = (): string => {
    switch (barometerStatus) {
      case SensorStatus.READY:
        return 'Pressure Verified ✓';
      case SensorStatus.SEARCHING:
        return 'Reading Pressure...';
      case SensorStatus.FAILED:
      case SensorStatus.UNAVAILABLE:
        return 'Pressure Unavailable';
      default:
        return 'Pressure Idle';
    }
  };

  return (
    <View style={styles.container}>
      {/* GPS Status */}
      <View style={[styles.statusCard, {borderColor: getGPSStatusColor()}]}>
        <View style={styles.statusHeader}>
          <View style={[styles.statusDot, {backgroundColor: getGPSStatusColor()}]} />
          <Text style={styles.statusTitle}>{getGPSStatusText()}</Text>
          {gpsStatus === SensorStatus.SEARCHING && (
            <ActivityIndicator size="small" color={getGPSStatusColor()} style={styles.spinner} />
          )}
        </View>

        {location && (
          <View style={styles.detailsContainer}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Coordinates:</Text>
              <Text style={styles.detailValue}>
                {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
              </Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Accuracy:</Text>
              <Text style={[styles.detailValue, {color: location.accuracy <= 20 ? '#10B981' : '#F59E0B'}]}>
                ±{location.accuracy.toFixed(1)} m
              </Text>
            </View>
            {distanceFromClassroom !== null && distanceFromClassroom !== undefined && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Distance:</Text>
                <Text style={[styles.detailValue, {color: distanceFromClassroom <= 50 ? '#10B981' : '#EF4444'}]}>
                  {distanceFromClassroom.toFixed(1)} m from classroom
                </Text>
              </View>
            )}
          </View>
        )}

        {gpsStatus === SensorStatus.SEARCHING && (
          <Text style={styles.hintText}>
            Ensure you have a clear view of the sky for better GPS signal
          </Text>
        )}

        {gpsStatus === SensorStatus.FAILED && (
          <Text style={styles.errorText}>
            Unable to acquire GPS location. Check location permissions.
          </Text>
        )}
      </View>

      {/* Barometer Status */}
      <View style={[styles.statusCard, {borderColor: getBarometerStatusColor()}]}>
        <View style={styles.statusHeader}>
          <View style={[styles.statusDot, {backgroundColor: getBarometerStatusColor()}]} />
          <Text style={styles.statusTitle}>{getBarometerStatusText()}</Text>
          {barometerStatus === SensorStatus.SEARCHING && (
            <ActivityIndicator size="small" color={getBarometerStatusColor()} style={styles.spinner} />
          )}
        </View>

        {pressure && (
          <View style={styles.detailsContainer}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Pressure:</Text>
              <Text style={styles.detailValue}>{pressure.pressure.toFixed(2)} hPa</Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Est. Altitude:</Text>
              <Text style={styles.detailValue}>{pressure.altitude.toFixed(1)} m</Text>
            </View>
          </View>
        )}

        {barometerStatus === SensorStatus.UNAVAILABLE && (
          <Text style={styles.hintText}>
            Barometer not available on this device. Floor verification will be skipped.
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 2,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  spinner: {
    marginLeft: 8,
  },
  detailsContainer: {
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
    fontSize: 13,
    color: '#6B7280',
  },
  detailValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
    textAlign: 'right',
  },
  hintText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    fontStyle: 'italic',
  },
  errorText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 8,
  },
});

export default LocationStatusIndicator;
