/**
 * Motion Prompt Component
 * Prompts user to perform head motion for liveness detection
 */
import React, {useState, useEffect} from 'react';
import {View, Text, StyleSheet, Animated} from 'react-native';
import {SensorStatus} from '../types';

interface MotionPromptProps {
  status: SensorStatus;
  progress: number; // 0-1
  motionDetected: boolean;
  samplingRate: number;
}

export const MotionPrompt: React.FC<MotionPromptProps> = ({
  status,
  progress,
  motionDetected,
  samplingRate,
}) => {
  const [animatedValue] = useState(new Animated.Value(0));

  /**
   * Animate head nodding icon
   */
  useEffect(() => {
    if (status === SensorStatus.SEARCHING || status === SensorStatus.READY) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(animatedValue, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(animatedValue, {
            toValue: 0,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [status]);

  const translateY = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -20],
  });

  const getStatusColor = (): string => {
    if (motionDetected) return '#10B981'; // Green
    if (status === SensorStatus.SEARCHING || status === SensorStatus.READY) return '#F59E0B'; // Yellow
    if (status === SensorStatus.FAILED) return '#EF4444'; // Red
    return '#9CA3AF'; // Gray
  };

  const getStatusText = (): string => {
    if (motionDetected) return 'Motion Detected ✓';
    if (status === SensorStatus.SEARCHING || status === SensorStatus.READY) return 'Nod your head gently';
    if (status === SensorStatus.FAILED) return 'Motion detection failed';
    return 'Waiting...';
  };

  return (
    <View style={styles.container}>
      {/* Animated Head Icon */}
      <Animated.View style={[styles.iconContainer, {transform: [{translateY}]}]}>
        <View style={[styles.headIcon, {borderColor: getStatusColor()}]}>
          <View style={styles.face}>
            <View style={styles.eye} />
            <View style={styles.eye} />
            <View style={styles.mouth} />
          </View>
        </View>
      </Animated.View>

      {/* Status Text */}
      <Text style={[styles.statusText, {color: getStatusColor()}]}>
        {getStatusText()}
      </Text>

      {/* Progress Bar */}
      {(status === SensorStatus.SEARCHING || status === SensorStatus.READY) && (
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${progress * 100}%`,
                  backgroundColor: motionDetected ? '#10B981' : '#F59E0B',
                },
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {Math.round(progress * 100)}% - {(progress * 2).toFixed(1)}s
          </Text>
        </View>
      )}

      {/* Motion Feedback */}
      {motionDetected && (
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackText}>✓ Sufficient motion detected</Text>
        </View>
      )}

      {/* Sampling Rate (Debug) */}
      {samplingRate > 0 && (
        <Text style={styles.debugText}>
          Sampling: {samplingRate.toFixed(1)} Hz
        </Text>
      )}

      {/* Instructions */}
      {!motionDetected && (status === SensorStatus.SEARCHING || status === SensorStatus.READY) && (
        <Text style={styles.instructionText}>
          Move your head up and down slowly
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  iconContainer: {
    marginBottom: 16,
  },
  headIcon: {
    width: 80,
    height: 100,
    borderRadius: 40,
    borderWidth: 4,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  face: {
    width: 60,
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
  },
  eye: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#1F2937',
    marginHorizontal: 8,
    position: 'absolute',
    top: 20,
  },
  mouth: {
    width: 30,
    height: 15,
    borderBottomLeftRadius: 15,
    borderBottomRightRadius: 15,
    borderWidth: 2,
    borderColor: '#1F2937',
    borderTopWidth: 0,
    position: 'absolute',
    bottom: 15,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  progressContainer: {
    width: '100%',
    marginTop: 8,
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 4,
  },
  feedbackContainer: {
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#D1FAE5',
    borderRadius: 8,
  },
  feedbackText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
  debugText: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 8,
  },
  instructionText: {
    fontSize: 13,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic',
  },
});

export default MotionPrompt;
