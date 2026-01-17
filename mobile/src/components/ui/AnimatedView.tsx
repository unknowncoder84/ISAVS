/**
 * AnimatedView Component (React Native)
 * Wrapper for animated entrance effects
 */
import React, {useEffect, useRef} from 'react';
import {Animated, ViewStyle} from 'react-native';
import {theme} from '../../styles/theme';

interface AnimatedViewProps {
  children: React.ReactNode;
  animation?: 'fadeIn' | 'slideUp' | 'scale';
  delay?: number;
  duration?: number;
  style?: ViewStyle;
}

export const AnimatedView: React.FC<AnimatedViewProps> = ({
  children,
  animation = 'fadeIn',
  delay = 0,
  duration = theme.animation.normal,
  style,
}) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: 1,
      duration,
      delay,
      useNativeDriver: true,
    }).start();
  }, [animatedValue, duration, delay]);

  const getAnimatedStyle = (): ViewStyle => {
    switch (animation) {
      case 'fadeIn':
        return {
          opacity: animatedValue,
        };
      case 'slideUp':
        return {
          opacity: animatedValue,
          transform: [
            {
              translateY: animatedValue.interpolate({
                inputRange: [0, 1],
                outputRange: [20, 0],
              }),
            },
          ],
        };
      case 'scale':
        return {
          opacity: animatedValue,
          transform: [
            {
              scale: animatedValue.interpolate({
                inputRange: [0, 1],
                outputRange: [0.9, 1],
              }),
            },
          ],
        };
      default:
        return {};
    }
  };

  return (
    <Animated.View style={[getAnimatedStyle(), style]}>
      {children}
    </Animated.View>
  );
};

export default AnimatedView;
