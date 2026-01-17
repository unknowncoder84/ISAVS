/**
 * ISAVS Mobile Design System
 * Blue/Purple Gradient Theme (Campus Connect Inspired)
 */

export const theme = {
  // Colors
  colors: {
    // Primary colors
    primary: '#3B82F6',      // Blue
    secondary: '#8B5CF6',    // Purple
    accent: '#A78BFA',       // Light Purple
    
    // Status colors
    success: '#10B981',      // Green
    warning: '#F59E0B',      // Orange
    danger: '#EF4444',       // Red
    info: '#3B82F6',         // Blue
    
    // Neutral colors
    white: '#FFFFFF',
    black: '#000000',
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
    
    // Background colors
    background: {
      primary: '#0F0D1A',
      secondary: '#1A1625',
      card: '#1A1625',
    },
    
    // Text colors
    text: {
      primary: '#FFFFFF',
      secondary: '#9CA3AF',
      tertiary: '#6B7280',
    },
  },
  
  // Gradients (for LinearGradient)
  gradients: {
    primary: {
      colors: ['#3B82F6', '#A78BFA'],
      start: { x: 0, y: 0 },
      end: { x: 1, y: 1 },
    },
    primaryHover: {
      colors: ['#2563EB', '#8B5CF6'],
      start: { x: 0, y: 0 },
      end: { x: 1, y: 1 },
    },
    card: {
      colors: ['rgba(59, 130, 246, 0.08)', 'rgba(167, 139, 250, 0.08)'],
      start: { x: 0, y: 0 },
      end: { x: 1, y: 1 },
    },
    success: {
      colors: ['#10B981', '#059669'],
      start: { x: 0, y: 0 },
      end: { x: 1, y: 1 },
    },
    danger: {
      colors: ['#EF4444', '#DC2626'],
      start: { x: 0, y: 0 },
      end: { x: 1, y: 1 },
    },
  },
  
  // Shadows
  shadows: {
    soft: {
      shadowColor: '#3B82F6',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 20,
      elevation: 4,
    },
    card: {
      shadowColor: '#000000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.08,
      shadowRadius: 12,
      elevation: 3,
    },
    glow: {
      shadowColor: '#3B82F6',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.25,
      shadowRadius: 30,
      elevation: 8,
    },
  },
  
  // Spacing
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  // Border radius
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    full: 9999,
  },
  
  // Typography
  typography: {
    fontFamily: {
      regular: 'System',
      medium: 'System',
      semibold: 'System',
      bold: 'System',
    },
    fontSize: {
      xs: 12,
      sm: 14,
      base: 16,
      lg: 18,
      xl: 20,
      '2xl': 24,
      '3xl': 30,
      '4xl': 36,
    },
    fontWeight: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
    },
  },
  
  // Animation durations
  animation: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
};

export type Theme = typeof theme;
