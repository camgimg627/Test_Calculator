export const provinces = [
  "Alberta",
  "British Columbia",
  "Manitoba",
  "New Brunswick",
  "Newfoundland and Labrador",
  "Northwest Territories",
  "Nova Scotia",
  "Nunavut",
  "Ontario",
  "Prince Edward Island",
  "Quebec",
  "Saskatchewan",
  "Yukon",
];

function calcProgressiveTax(amount, brackets) {
  if (amount <= 0) {
    return 0;
  }

  let tax = 0;
  let previousCap = 0;

  for (const bracket of brackets) {
    const cap = bracket.upTo ?? amount;
    if (amount <= previousCap) {
      break;
    }

    const taxable = Math.min(amount, cap) - previousCap;
    if (taxable > 0) {
      tax += taxable * bracket.rate;
    }

    previousCap = cap;
  }

  return tax;
}

function lttOntario(purchasePrice) {
  return calcProgressiveTax(purchasePrice, [
    { upTo: 55_000, rate: 0.005 },
    { upTo: 250_000, rate: 0.01 },
    { upTo: 400_000, rate: 0.015 },
    { upTo: 2_000_000, rate: 0.02 },
    { upTo: null, rate: 0.025 },
  ]);
}

function pttBritishColumbia(purchasePrice) {
  return calcProgressiveTax(purchasePrice, [
    { upTo: 200_000, rate: 0.01 },
    { upTo: 2_000_000, rate: 0.02 },
    { upTo: 3_000_000, rate: 0.03 },
    { upTo: null, rate: 0.05 },
  ]);
}

function lttManitoba(purchasePrice) {
  return calcProgressiveTax(purchasePrice, [
    { upTo: 30_000, rate: 0 },
    { upTo: 90_000, rate: 0.005 },
    { upTo: 150_000, rate: 0.01 },
    { upTo: 200_000, rate: 0.015 },
    { upTo: null, rate: 0.02 },
  ]);
}

function lttQuebec(purchasePrice) {
  return calcProgressiveTax(purchasePrice, [
    { upTo: 52_800, rate: 0.005 },
    { upTo: 264_000, rate: 0.01 },
    { upTo: 527_900, rate: 0.015 },
    { upTo: null, rate: 0.02 },
  ]);
}

export function calculateLandTransferTax({
  province,
  city = "",
  purchasePrice = 0,
  nsRate = 1.5,
  nlRate = 0.4,
  bcForeignBuyer = false,
  isFirstTimeBuyer = false,
  salePrice = null,
} = {}) {
  const price = Number.isFinite(Number(purchasePrice)) ? Math.max(Number(purchasePrice), 0) : 0;
  const normalizedCity = city.trim().toLowerCase();
  const notes = [];
  let provinceTax = 0;
  let municipalTax = 0;

  switch (province) {
    case "Ontario":
      provinceTax = lttOntario(price);
      if (normalizedCity === "toronto") {
        municipalTax = lttOntario(price);
        notes.push("Toronto Municipal Land Transfer Tax is added on top of Ontario LTT.");
      } else {
        notes.push("Ontario LTT calculated using common provincial brackets.");
      }
      if (isFirstTimeBuyer) {
        notes.push("First-time buyer rebates are not applied in this version.");
      }
      break;

    case "British Columbia":
      provinceTax = pttBritishColumbia(price);
      if (bcForeignBuyer) {
        municipalTax += price * 0.2;
        notes.push("BC foreign buyer additional tax toggle is a placeholder; rates and areas vary.");
      }
      notes.push("BC PTT calculated using common brackets.");
      if (isFirstTimeBuyer) {
        notes.push("First-time buyer exemptions are not applied in this version.");
      }
      break;

    case "Manitoba":
      provinceTax = lttManitoba(price);
      notes.push("Manitoba LTT calculated using the common bracket schedule.");
      break;

    case "Quebec":
      provinceTax = lttQuebec(price);
      notes.push("Quebec Welcome Tax estimated with commonly used thresholds.");
      if (isFirstTimeBuyer) {
        notes.push("Municipal or provincial programs and rebates are not applied in this version.");
      }
      break;

    case "New Brunswick":
      provinceTax = price * 0.01;
      notes.push("NB Real Property Transfer Tax estimated as 1% of purchase price.");
      break;

    case "Prince Edward Island":
      provinceTax = price * 0.01;
      notes.push("PEI Real Property Transfer Tax estimated as 1% of purchase price.");
      break;

    case "Nova Scotia":
      provinceTax = price * (Math.max(Number(nsRate) || 0, 0) / 100);
      notes.push("Nova Scotia deed transfer tax varies by municipality; using the entered rate.");
      break;

    case "Newfoundland and Labrador":
      provinceTax = price * (Math.max(Number(nlRate) || 0, 0) / 100);
      notes.push("NL fees vary; using the entered simplified proxy rate.");
      break;

    case "Alberta":
    case "Saskatchewan":
    case "Yukon":
    case "Northwest Territories":
    case "Nunavut":
      notes.push("This calculator returns $0 for LTT/PTT because these jurisdictions typically use land title or registration fees instead.");
      break;

    default:
      notes.push("Select a province or territory to calculate the estimate.");
  }

  if (salePrice !== null && salePrice !== "") {
    notes.push("Sale price is captured for future special-tax modules; no sale-price-based tax is calculated yet.");
  }

  return {
    provinceTax,
    municipalTax,
    totalTax: provinceTax + municipalTax,
    notes,
  };
}

export function formatMoney(value) {
  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
  }).format(value);
}
