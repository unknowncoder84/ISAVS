/**
 * GradientButton Component (React Native)
 * Blue/Purple gradient button with animations
 */
import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {theme} from '../../styles/theme';

interface GradientButtonProps {
  onPress: () => void;
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  variant?: 'primary' | 'success' | 'danger';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const GradientButton: React.FC<GradientButtonProps> = ({
  onPress,
  children,
  disabled = false,
  loading = false,
  size = 'md',
  fullWidth = false,
  variant = 'primary',
  style,
  textStyle,
}) => {
  const gradient = theme.gradients[variant];
  const isDisabled = disabled || loading;

  const buttonStyle: ViewStyle = {
    ...styles.button,
    ...styles[`button_${size}`],
    ...(fullWidth && styles.fullWidth),
    ...(isDisabled && styles.disabled),
    ...style,
  };

  const textStyles: TextStyle = {
    ...styles.text,
    ...styles[`text_${size}`],
    ...textStyle,
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.8}
      style={buttonStyle}>
      <LinearGradient
        colors={gradient.colors}
        start={gradient.start}
        end={gradient.end}
        style={styles.gradient}>
        {loading ? (
          <ActivityIndicator color={theme.colors.white} />
        ) : (
          <Text style={textStyles}>{children}</Text>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
    ...theme.shadows.soft,
  },
  button_sm: {
    height: 36,
  },
  button_md: {
    height: 48,
  },
  button_lg: {
    height: 56,
  },
  fullWidth: {
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
  gradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
  },
  text: {
    color: theme.colors.white,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  text_sm: {
    fontSize: theme.typography.fontSize.sm,
  },
  text_md: {
    fontSize: theme.typography.fontSize.base,
  },
  text_lg: {
    fontSize: theme.typography.fontSize.lg,
  },
});

export default GradientButton;
