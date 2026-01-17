/**
 * Verification Result Screen
 * Displays detailed verification results with factor breakdown
 */
import React from 'react';
import {View, Text, StyleSheet, ScrollView, TouchableOpacity} from 'react';
import {SensorVerificationResponse} from '../types';

interface VerificationResultScreenProps {
  result: SensorVerificationResponse;
  onClose: () => void;
}

export const VerificationResultScreen: React.FC<VerificationResultScreenProps> = ({
  result,
  onClose,
}) => {
  const {success, message, factors} = result;

  /**
   * Render factor row
   */
  const renderFactor = (
    label: string,
    passed: boolean,
    value?: number,
    unit?: string
  ) => {
    return (
      <View style={styles.factorRow}>
        <View style={styles.factorLeft}>
          <View style={[styles.factorIcon, {backgroundColor: passed ? '#10B981' : '#EF4444'}]}>
            <Text style={styles.factorIconText}>{passed ? '✓' : '✗'}</Text>
          </View>
          <Text style={styles.factorLabel}>{label}</Text>
        </View>
        {value !== undefined && (
          <Text style={[styles.factorValue, {color: passed ? '#10B981' : '#EF4444'}]}>
            {value.toFixed(2)} {unit}
          </Text>
        )}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Overall Result */}
        <View style={[styles.resultCard, {backgroundColor: success ? '#D1FAE5' : '#FEE2E2'}]}>
          <View style={[styles.resultIcon, {backgroundColor: success ? '#10B981' : '#EF4444'}]}>
            <Text style={styles.resultIconText}>{success ? '✓' : '✗'}</Text>
          </View>
          <Text style={styles.resultTitle}>
            {success ? 'Verification Successful' : 'Verification Failed'}
          </Text>
          <Text style={styles.resultMessage}>{message}</Text>
        </View>

        {/* Factor Breakdown */}
        <View style={styles.factorsCard}>
          <Text style={styles.factorsTitle}>Verification Factors</Text>

          {/* Face Recognition */}
          {renderFactor(
            'Face Recognition',
            factors.face_verified,
            factors.face_confidence,
            '%'
          )}

          {/* Liveness Detection */}
          {renderFactor('Liveness Detection', factors.liveness_passed)}

          {/* ID Verification */}
          {renderFactor('ID Verification', factors.id_verified)}

          {/* OTP Verification */}
          {renderFactor('OTP Verification', factors.otp_verified)}

          {/* BLE Proximity */}
          {renderFactor(
            'BLE Proximity',
            factors.ble_verified,
            factors.ble_rssi,
            'dBm'
          )}

          {/* GPS Geofence */}
          {renderFactor(
            'GPS Geofence',
            factors.geofence_verified,
            factors.distance_meters,
            'm'
          )}

          {/* Barometer */}
          {renderFactor(
            'Barometric Pressure',
            factors.barometer_verified,
            factors.pressure_diff,
            'hPa'
          )}

          {/* Motion Correlation */}
          {renderFactor(
            'Motion Correlation',
            factors.motion_verified,
            factors.motion_correlation,
            ''
          )}
        </View>

        {/* Summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Summary</Text>
          <Text style={styles.summaryText}>
            {success
              ? 'All verification factors passed. Your attendance has been marked successfully.'
              : 'One or more verification factors failed. Please try again or contact faculty for assistance.'}
          </Text>
        </View>

        {/* Close Button */}
        <TouchableOpacity
          style={[styles.closeButton, {backgroundColor: success ? '#10B981' : '#3B82F6'}]}
          onPress={onClose}>
          <Text style={styles.closeButtonText}>
            {success ? 'Done' : 'Try Again'}
          </Text>
        </TouchableOpacity>
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
  resultCard: {
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
  },
  resultIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  resultIconText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  resultMessage: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  factorsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  factorsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  factorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  factorLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  factorIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  factorIconText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  factorLabel: {
    fontSize: 16,
    color: '#1F2937',
  },
  factorValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  summaryText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  closeButton: {
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  closeButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});

export default VerificationResultScreen;
