import { createBrowserRouter } from 'react-router';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
// import Alerts from './pages/Alerts';
import Clips from './pages/Clips';
// import Status from './pages/Status';
// import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';

export const router = createBrowserRouter([
  {
    path: '/login',
    Component: Login,
  },
  {
    path: '/register',
    Component: Register,
  },
  {
    path: '/',
    Component: Layout,
    children: [
      {
        index: true,
        Component: Dashboard,
      },

      {
        path: 'clips',
        Component: Clips,
      },

      // =========================
      // DISABLED ROUTES
      // =========================
      /*
      {
        path: 'alerts',
        Component: Alerts,
      },
      {
        path: 'status',
        Component: Status,
      },
      {
        path: 'settings',
        Component: Settings,
      },
      */
    ],
  },
]);
