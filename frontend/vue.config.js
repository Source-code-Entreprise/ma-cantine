const BundleTracker = require("webpack-bundle-tracker")
const debug = !process.env.DEBUG || process.env.DEBUG === "True"
const publicPath = debug ? "https://8080-sourcecodeent-macantine-65ay5qejdg9.ws-eu115.gitpod.io/" : "/static/"

module.exports = {
  transpileDependencies: ["vuetify"],
  runtimeCompiler: true,
  publicPath: publicPath,
  outputDir: "./dist/",

  configureWebpack: {
    devtool: "source-map",
  },

  css: {
    sourceMap: true,
  },

  chainWebpack: (config) => {
    config.optimization.splitChunks(false)

    config.plugin("BundleTracker").use(BundleTracker, [{ path: "../frontend/", filename: "webpack-stats.json" }])

    config.resolve.alias.set("__STATIC__", "static")

    config.devServer
      .public("https://8080-sourcecodeent-macantine-65ay5qejdg9.ws-eu115.gitpod.io/")
      .host("0.0.0.0")
      //.port(8080)
      .hotOnly(true)
      .watchOptions({ poll: 1000 })
      .https(false)
      // eslint-disable-next-line no-useless-escape
      .headers({ "Access-Control-Allow-Origin": ["*"] })
      .disableHostCheck(true)
  },
}
