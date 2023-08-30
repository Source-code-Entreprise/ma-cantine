import { createRouter, createWebHistory } from "vue-router"
import store from "@/store"
import Constants from "@/constants"
import LandingPage from "@/views/LandingPage"
import AccessibilityDeclaration from "@/views/AccessibilityDeclaration"
import FaqPage from "@/views/FaqPage"
import ContactPage from "@/views/ContactPage"

const routes = [
  // {
  //   path: "/",
  //   meta: {
  //     home: true,
  //   },
  // },
  {
    // path: "/accueil",
    path: "/",
    name: "LandingPage",
    component: LandingPage,
  },
  {
    path: "/a11y",
    name: "AccessibilityDeclaration",
    component: AccessibilityDeclaration,
  },
  {
    path: "/faq/",
    name: "FaqPage",
    component: FaqPage,
    meta: {
      title: "Foire aux questions",
    },
    sitemapGroup: Constants.SitemapGroups.SITE,
  },
  {
    path: "/contact",
    name: "ContactPage",
    component: ContactPage,
    meta: {
      title: "Contactez-nous",
    },
    sitemapGroup: Constants.SitemapGroups.SITE,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to /*, from, savedPosition*/) {
    if (to.hash) return { selector: to.hash, offset: { y: 200 } }
    // if (to.name === from.name && this.app.$vuetify.breakpoint.mdAndUp) return savedPosition
    return { x: 0, y: 0 }
  },
})

function chooseAuthorisedRoute(to, from, next) {
  if (!store.state.initialDataLoaded) {
    store
      .dispatch("fetchInitialData")
      .then(() => chooseAuthorisedRoute(to, from, next))
      .catch((e) => {
        console.error(`An error occurred: ${e}`)
        next({ name: "LandingPage" })
      })
  } else {
    if (to.meta.home && store.state.loggedUser && !store.state.loggedUser.isDev) next({ name: "ManagementPage" })
    else if (to.meta.home && store.state.loggedUser && store.state.loggedUser.isDev) next({ name: "DeveloperPage" })
    else if (to.meta.home) next({ name: "LandingPage" })
    else if (!to.meta.authenticationRequired || store.state.loggedUser) next()
    else window.location.href = `/s-identifier?next=${to.path}`
  }
}

router.beforeEach((to, from, next) => {
  chooseAuthorisedRoute(to, from, next)
})

export { router, routes }
