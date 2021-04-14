import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '@/views/LandingPage';
import DiagnosticPage from '@/views/DiagnosticPage';
import KeyMeasuresPage from '@/views/KeyMeasuresPage';
import KeyMeasuresHome from '@/views/KeyMeasuresPage/KeyMeasuresHome';
import KeyMeasurePage from '@/views/KeyMeasuresPage/KeyMeasurePage';
import GeneratePosterPage from '@/views/GeneratePosterPage';
import CanteensPage from '@/views/CanteensPage';
import CanteensHome from '@/views/CanteensPage/CanteensHome';
import LegalNotices from '@/views/LegalNotices';

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPage,
  },
  {
    path: '/diagnostique',
    name: 'DiagnosticPage',
    component: DiagnosticPage,
    meta: {
      title: "M'auto-évaluer"
    }
  },
  {
    path: '/creation-affiche',
    name: 'GeneratePosterPage',
    component: GeneratePosterPage,
  },
  {
    path: '/mesures-phares',
    name: 'KeyMeasuresPage',
    component: KeyMeasuresPage,
    meta: {
      title: "Les 5 mesures phares de la loi EGAlim"
    },
    children: [
      {
        path: '',
        name: 'KeyMeasuresHome',
        component: KeyMeasuresHome,
      },
      {
        path: ':id',
        name: 'KeyMeasurePage',
        component: KeyMeasurePage,
        props: true,
      }
    ]
  },
  {
    path: '/nos-cantines',
    name: 'CanteensPage',
    component: CanteensPage,
    children: [
      {
        path: '',
        name: 'CanteensHome',
        component: CanteensHome,
      },
    ]
  },
  {
    path: '/mentions-legales',
    name: 'LegalNotices',
    component: LegalNotices,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        top: 80
      }
    } else {
      return {
        top: 0
      };
    }
  }
});

export default router;
