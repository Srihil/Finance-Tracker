import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator }      from '@react-navigation/stack';
import { createBottomTabNavigator }  from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { ActivityIndicator, View }   from 'react-native';

import { useAuth }    from '../context/AuthContext';
import { COLORS }     from '../constants';

// ── Auth Screens ──────────────────────────────────────────────
import LoginScreen    from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// ── App Screens ───────────────────────────────────────────────
import DashboardScreen      from '../screens/dashboard/DashboardScreen';
import TransactionListScreen from '../screens/transactions/TransactionListScreen';
import AddTransactionScreen  from '../screens/transactions/AddTransactionScreen';
import ProfileScreen         from '../screens/dashboard/ProfileScreen';

const Stack  = createStackNavigator();
const Tab    = createBottomTabNavigator();

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      headerShown: false,
      tabBarStyle: {
        backgroundColor: COLORS.dark,
        borderTopColor : COLORS.card,
        height         : 60,
        paddingBottom  : 8,
      },
      tabBarActiveTintColor  : COLORS.primary,
      tabBarInactiveTintColor: COLORS.gray,
      tabBarIcon: ({ color, size, focused }) => {
        const icons = {
          Dashboard   : focused ? 'home'            : 'home-outline',
          Transactions: focused ? 'list'             : 'list-outline',
          Add         : focused ? 'add-circle'       : 'add-circle-outline',
          Profile     : focused ? 'person'           : 'person-outline',
        };
        return (
          <Ionicons
            name={icons[route.name]}
            size={route.name === 'Add' ? 30 : size}
            color={route.name === 'Add' ? COLORS.primary : color}
          />
        );
      },
    })}
  >
    <Tab.Screen name="Dashboard"    component={DashboardScreen} />
    <Tab.Screen name="Transactions" component={TransactionListScreen} />
    <Tab.Screen name="Add"          component={AddTransactionScreen} />
    <Tab.Screen name="Profile"      component={ProfileScreen} />
  </Tab.Navigator>
);

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login"    component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const AppNavigator = () => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <View style={{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: COLORS.dark,
      }}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default AppNavigator;