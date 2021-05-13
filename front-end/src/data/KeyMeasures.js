import keyMeasures from "@/data/key-measures.json";

function findSubMeasure(id) {
  for (let measureIdx = 0; measureIdx < keyMeasures.length; measureIdx++) {
    const measure = keyMeasures[measureIdx];
    const subMeasure = measure.subMeasures.find((subMeasure) => subMeasure.id === id);
    if(subMeasure) { return subMeasure; }
  }
}

const defaultFlatDiagnostic = {
  valueBio: null,
  valueFairTrade: null,
  valueSustainable: null,
  valueTotal: null,
  hasMadeWasteDiagnostic: false,
  hasMadeWastePlan: false,
  wasteActions: [],
  hasDonationAgreement: false,
  hasMadeDiversificationPlan: false,
  vegetarianFrequency: null,
  vegetarianMenuType: null,
  cookingFoodContainersSubstituted: false,
  serviceFoodContainersSubstituted: false,
  waterBottlesSubstituted: false,
  disposableUtensilsSubstituted: false,
  communicationSupports: [],
  communicationSupportLink: null,
  communicateOnFoodPlan: false,
};

function defaultFlatDiagnosticWithYear(diagnostic, year) {
  let diagnosticCopy = JSON.parse(JSON.stringify(diagnostic));
  diagnosticCopy.year = year;
  return diagnosticCopy;
}

const defaultFlatDiagnostics = [
  defaultFlatDiagnosticWithYear(defaultFlatDiagnostic, 2019),
  defaultFlatDiagnosticWithYear(defaultFlatDiagnostic, 2020)
];

async function getDiagnostics() {
  let diagnostics, hasSavedResults;

  const jwt = localStorage.getItem('jwt');
  if(jwt) {
    const response = await fetch(`${process.env.VUE_APP_API_URL}/get-diagnostics-by-canteen`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+jwt
      }
    });
    if(response.status === 200) {
      diagnostics = await response.json();
      hasSavedResults = !!diagnostics.latest;
    }
  }

  if(!hasSavedResults) {
    const localDiagnostics = (getLocalDiagnostics() || defaultFlatDiagnostics).
      sort((earlierDiag, laterDiag) => laterDiag.year - earlierDiag.year);
    diagnostics = {
      latest: localDiagnostics[0],
      previous: localDiagnostics[1]
    }
  }

  return {
    diagnostics,
    hasResults: hasSavedResults || !!localStorage.getItem(LOCAL_FLAT_KEY) || !!localStorage.getItem('diagnostics')
  };
}

const LOCAL_FLAT_KEY = 'flatDiagnostics';

// returns nothing if no local diagnostics
function getLocalDiagnostics() {
  let flatDiagnostics, diagnostics;
  const hasFlatDiagnostics = !!localStorage.getItem(LOCAL_FLAT_KEY);
  const hasStructuredDiagnostics = !!localStorage.getItem('diagnostics');
  const diagnosticsString = localStorage.getItem(LOCAL_FLAT_KEY) || localStorage.getItem('diagnostics');
  if(diagnosticsString) {
    diagnostics = JSON.parse(diagnosticsString);
  }

  // TODO: remove when our testers are using the new structure
  if(!hasFlatDiagnostics && hasStructuredDiagnostics) {
    if(Object.keys(diagnostics["gaspillage-alimentaire"]).indexOf("hasCovenant") !== -1) {
      diagnostics["gaspillage-alimentaire"].hasDonationAgreement = diagnostics["gaspillage-alimentaire"].hasCovenant;
      delete diagnostics["gaspillage-alimentaire"].hasCovenant;
    }
    if(Object.keys(diagnostics["information-des-usagers"]).indexOf("communicationSupport") !== -1) {
      diagnostics["information-des-usagers"].communicationSupports = diagnostics["information-des-usagers"].communicationSupport;
      delete diagnostics["information-des-usagers"].communicationSupport;
    }
    flatDiagnostics = flattenDiagnostics(diagnostics, 2020);
  } else if(hasFlatDiagnostics) {
    flatDiagnostics = diagnostics;
  }

  return flatDiagnostics;
}

// TODO: remove when our testers are using the new structure
function flattenDiagnostics(diags, defaultYear) {
  let flattened = [{ year: defaultYear }];
  for (const [measureKey, measureData] of Object.entries(diags)) {
    if(measureKey === 'qualite-des-produits') {
      for (const [yearKey, yearData] of Object.entries(measureData)) {
        const year = parseInt(yearKey, 10);
        if(year === defaultYear) {
          flattened[0] = {
            ...flattened[0],
            ...yearData
          };
        } else {
          yearData.year = year;
          flattened.push(yearData);
        }
      }
    } else {
      flattened[0] = {
        ...flattened[0],
        ...measureData
      };
    }
  }
  return preprocessDiagnostics(flattened);
}

function preprocessDiagnostics(diagnosticsArray) {
  diagnosticsArray.forEach(entry => {
    for (const [key, data] of Object.entries(entry)) {
      if(data === null || data === "") {
        delete entry[key];
      } else if(key === 'year') {
        // year expected to be number everywhere
        entry[key] = parseInt(entry[key], 10);
      }
    }
  });
  return diagnosticsArray;
}

async function saveDiagnostic(diagnostic) {
  const { diagnostics: diagnosticsObject } = await getDiagnostics();
  let diagnostics = [ diagnosticsObject.latest, diagnosticsObject.previous ];
  const idx = diagnostics.findIndex(d => d.year === diagnostic.year);
  // at the moment, the diagnostics are defaulted to guarantee a year match
  diagnostics[idx] = diagnostic;
  return saveDiagnosticsArray(diagnostics);
}

function saveDiagnostics(diagnosticsObject) {
  return saveDiagnosticsArray([ diagnosticsObject.latest, diagnosticsObject.previous ]);
}

async function saveDiagnosticsArray(diagnostics) {
  diagnostics = preprocessDiagnostics(diagnostics);
  let isSaved = false;
  const jwt = localStorage.getItem('jwt');
  if(jwt) {
    const response = await fetch(`${process.env.VUE_APP_API_URL}/save-diagnostics`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+jwt
      },
      body: JSON.stringify({
        diagnostics
      })
    });
    if(response.status === 201) {
      isSaved = true;
      deleteLocalDiagnostics();
    }
  }

  if(!isSaved) {
    localStorage.setItem(LOCAL_FLAT_KEY, JSON.stringify(diagnostics));
  }
}

// doen't return default values if data doesn't exist
async function getDiagnosticsForDashboard() {
  const diagnosticInfo = await getDiagnostics();
  if(diagnosticInfo.hasResults) {
    return diagnosticInfo.diagnostics;
  }
}

// returns default values if data doesn't exist
async function getDiagnosticsForDiagnosticForm() {
  const diagnosticInfo = await getDiagnostics();
  return diagnosticInfo.diagnostics;
}

function getDiagnosticsForCanteenSummary(canteen) {
  return canteen.diagnostics.find(diagnostic => diagnostic.year === canteen.timePeriod);
}

async function getDiagnosticsForPoster() {
  const diagnosticsInfo = await getDiagnostics();
  return diagnosticsInfo.diagnostics.latest;
}

function deleteLocalDiagnostics() {
  localStorage.removeItem(LOCAL_FLAT_KEY);
  // TODO: remove when our testers are using the new structure
  localStorage.removeItem('diagnostics');
}

export {
  keyMeasures,
  findSubMeasure,
  saveDiagnostic,
  saveDiagnostics,
  getDiagnostics,
  getLocalDiagnostics,
  deleteLocalDiagnostics,
  defaultFlatDiagnostics,
  getDiagnosticsForDashboard,
  getDiagnosticsForDiagnosticForm,
  getDiagnosticsForCanteenSummary,
  getDiagnosticsForPoster,
};
