import assert from "node:assert/strict";
import test from "node:test";

import { calculateLandTransferTax, formatMoney } from "../public/taxCalculator.mjs";

test("calculates Ontario and Toronto land transfer tax on the same bracket schedule", () => {
  const result = calculateLandTransferTax({
    province: "Ontario",
    city: "Toronto",
    purchasePrice: 750_000,
  });

  assert.equal(result.provinceTax, 11_475);
  assert.equal(result.municipalTax, 11_475);
  assert.equal(result.totalTax, 22_950);
});

test("calculates BC property transfer tax with optional foreign buyer add-on", () => {
  const result = calculateLandTransferTax({
    province: "British Columbia",
    purchasePrice: 2_500_000,
    bcForeignBuyer: true,
  });

  assert.equal(result.provinceTax, 53_000);
  assert.equal(result.municipalTax, 500_000);
  assert.equal(result.totalTax, 553_000);
});

test("uses entered municipal/proxy rates for Nova Scotia and Newfoundland and Labrador", () => {
  assert.equal(
    calculateLandTransferTax({
      province: "Nova Scotia",
      purchasePrice: 400_000,
      nsRate: 1.25,
    }).totalTax,
    5_000,
  );

  assert.equal(
    calculateLandTransferTax({
      province: "Newfoundland and Labrador",
      purchasePrice: 400_000,
      nlRate: 0.4,
    }).totalTax,
    1_600,
  );
});

test("formats Canadian dollar amounts", () => {
  assert.equal(formatMoney(22_950), "$22,950.00");
});
