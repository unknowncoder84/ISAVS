/**
 * GradientCard Component (React Native)
 * Card with glass-morphism effect and gradient background
 */
import React from 'react';
import {View, StyleSheet, ViewStyle} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {theme} from '../../styles/theme';

interface GradientCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  gradient?: boolean;
  padding?: keyof typeof theme.spacing;
}

export const GradientCard: React.FC<GradientCardProps> = ({
  children,
  style,
  gradient = false,
  padding = 'md',
}) => {
  const cardStyle: ViewStyle = {
    ...styles.card,
    padding: theme.spacing[padding],
    ...style,
  };

  if (gradient) {
    return (
      <View style={cardStyle}>
        <LinearGradient
          colors={theme.gradients.card.colors}
          start={theme.gradients.card.start}
          end={theme.gradients.card.end}
          style={styles.gradientBackground}>
          <View style={styles.content}>{children}</View>
        </LinearGradient>
      </View>
    );
  }

  return <View style={cardStyle}>{children}</View>;
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: theme.borderRadius.xl,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    ...theme.shadows.card,
    overflow: 'hidden',
  },
  gradientBackground: {
    flex: 1,
    borderRadius: theme.borderRadius.xl,
  },
  content: {
    flex: 1,
  },
});

export default GradientCard;
