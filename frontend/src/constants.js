export default Object.freeze({
  LoadingStatus: {
    LOADING: 1,
    SUCCESS: 2,
    ERROR: 3,
    IDLE: 4,
  },
  DefaultDiagnostics: {
    id: null,
    year: null,
    valueBioHt: null,
    valueSustainableHt: null,
    valueTotalHt: null,
    hasWasteDiagnostic: null,
    hasWastePlan: null,
    wasteActions: [],
    hasDonationAgreement: null,
    hasDiversificationPlan: null,
    vegetarianWeeklyRecurrence: null,
    vegetarianMenuType: null,
    vegetarianMenuBases: [],
    cookingPlasticSubstituted: null,
    servingPlasticSubstituted: null,
    plasticBottlesSubstituted: null,
    plasticTablewareSubstituted: null,
    communicationSupports: [],
    communicationSupportUrl: null,
    communicatesOnFoodPlan: null,
  },
  ManagementTypes: [
    {
      text: "Directe",
      value: "direct",
    },
    {
      text: "Concédée",
      value: "conceded",
    },
  ],
  ProductFamilies: {
    VIANDES_VOLAILLES: { text: "Viandes et volailles fraîches et surgelées", color: "pink darken-4" },
    CHARCUTERIE: { text: "Charcuterie", shortText: "Charcut- erie", color: "pink darken-4" },
    PRODUITS_DE_LA_MER: {
      text: "Produits aquatiques frais et surgelés",
      shortText: "Produits aqua- tiques frais et surgelés",
      color: "blue darken-3",
    },
    FRUITS_ET_LEGUMES: { text: "Fruits et légumes frais et surgelés", color: "green darken-3" },
    PRODUITS_LAITIERS: { text: "BOF (Produits laitiers, beurre et œufs)", color: "deep-orange darken-4" },
    BOULANGERIE: {
      text: "Boulangerie / Pâtisserie fraîches",
      shortText: "Boulan- gerie / Pâtisserie fraîches",
      color: "deep-purple darken-3",
    },
    BOISSONS: { text: "Boissons", color: "green darken-4" },
    AUTRES: { text: "Autres produits frais, surgelés et d’épicerie", color: "grey darken-3" },
  },
  Characteristics: {
    // NB: the order of these can affect the aesthetics of the display on PurchasePage, esp for long texts
    BIO: { text: "Bio" },
    LABEL_ROUGE: { text: "Label rouge" },
    AOCAOP: { text: "AOC / AOP", longText: "Appellation d'origine (AOC / AOP)" },
    ICP: { text: "IGP", longText: "Indication géographique protégée (IGP)" },
    STG: { text: "STG", longText: "Spécialité traditionnelle garantie (STG)" },
    PECHE_DURABLE: { text: "Pêche durable" },
    RUP: { text: "RUP", longText: "Région ultrapériphérique (RUP)" },
    COMMERCE_EQUITABLE: { text: "Commerce équitable" },
    HVE: { text: "HVE", longText: "HVE ou certification environnementale de niveau 2" },
    FERMIER: { text: "Fermier", longText: "Mention « fermier » ou « produit de la ferme » ou « produit à la ferme »" },
    EQUIVALENTS: {
      text: "Produits équivalents",
      longText: "Produits équivalents aux produits bénéficiant de ces mentions ou labels",
    },
    EXTERNALITES: {
      text: "Externalités environnementales",
      longText:
        "Produits acquis prenant en compte les coûts imputés aux externalités environnementales pendant son cycle de vie",
    },
    PERFORMANCE: {
      text: "Performance environnementale",
      longText: "Produits acquis sur la base de leurs performances en matière environnementale",
    },
    FRANCE: { text: "Provenance France" },
    SHORT_DISTRIBUTION: { text: "Circuit-court" },
    LOCAL: { text: "Local" },
  },
  TeledeclarationCharacteristics: {
    // NB: the order of these can affect the aesthetics of the display on PurchasePage, esp for long texts
    BIO: { text: "Bio" },
    LABEL_ROUGE: { text: "Label rouge" },
    AOCAOP_IGP_STG: { text: "AOC / AOP / IGP / STG", longText: "AOC / AOP / IGP / STG" },
    PECHE_DURABLE: { text: "Pêche durable" },
    RUP: { text: "RUP", longText: "Région ultrapériphérique (RUP)" },
    COMMERCE_EQUITABLE: { text: "Commerce équitable" },
    HVE: { text: "HVE", longText: "HVE ou certification environnementale de niveau 2" },
    FERMIER: { text: "Fermier", longText: "Mention « fermier » ou « produit de la ferme » ou « produit à la ferme »" },
    EQUIVALENTS: {
      text: "Produits équivalents",
      longText: "Produits équivalents aux produits bénéficiant de ces mentions ou labels",
    },
    EXTERNALITES: {
      text: "Externalités environnementales",
      longText:
        "Produits acquis prenant en compte les coûts imputés aux externalités environnementales pendant son cycle de vie",
    },
    PERFORMANCE: {
      text: "Performance environnementale",
      longText: "Produits acquis sur la base de leurs performances en matière environnementale",
    },
    FRANCE: { text: "Provenance France" },
    SHORT_DISTRIBUTION: { text: "Circuit-court" },
    LOCAL: { text: "Local" },
  },
  LocalDefinitions: {
    AUTOUR_SERVICE: { text: "200 km autour du lieu de service", value: "AUTOUR_SERVICE" },
    DEPARTMENT: { text: "Provenant du même département", value: "DEPARTMENT" },
    REGION: { text: "Provenant de la même région", value: "REGION" },
    AUTRE: { text: "Autre", value: "AUTRE" },
  },
  TrackingParams: ["mtm_source", "mtm_campaign", "mtm_medium"],
  Jobs: [
    {
      text: "Gestionnaire d'établissement",
      value: "ESTABLISHMENT_MANAGER",
    },
    {
      text: "Direction achat société de restauration",
      value: "CATERING_PURCHASES_MANAGER",
    },
    {
      text: "Responsable d'achats en gestion directe",
      value: "DIRECT_PURCHASES_MANAGER",
    },
    {
      text: "Responsable de plusieurs établissements (type cuisine centrale)",
      value: "CENTRAL_MANAGER",
    },
    {
      text: "Responsable de plusieurs établissements (SRC)",
      value: "MANY_ESTABLISHMENTS_MANAGER",
    },
    {
      text: "Autre (spécifiez)",
      value: "OTHER",
    },
  ],
  UserSources: [
    {
      text: "Webinaire",
      value: "WEBINAIRE",
    },
    {
      text: "Recherche web",
      value: "WEB_SEARCH",
    },
    {
      text: "Communication institutionnelle (DRAAF, association régionale)",
      value: "INSTITUTION",
    },
    {
      text: "Bouche à oreille",
      value: "WORD_OF_MOUTH",
    },
    {
      text: "Réseaux sociaux",
      value: "SOCIAL_MEDIA",
    },
    {
      text: "Autre (spécifiez)",
      value: "OTHER",
    },
  ],
})
