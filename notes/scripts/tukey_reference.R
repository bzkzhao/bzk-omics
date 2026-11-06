# Reference values for the Tukey HSD build (walk/PREREG-PXD032267-gate.md §4, instrument validation).
#
# Written and run OUTSIDE the session that implements the test, so that the implementation and its
# oracle cannot share a misreading of which pair, which error term or which df. Base R only, no
# packages. Output: tests/fixtures/r_tukey_reference.csv, one row per reference value, full precision.
#
#     Rscript notes/scripts/tukey_reference.R            # from the repository root
#
# Cases. ToothGrowth restricted to dose 0.5 and 1.0 gives a balanced 2 x 2 (supp x dose), the shape
# of the gate's design:
#   tg_n10  all 10 per cell
#   tg_n3   the first 3 rows of each cell in dataset order, matching the gate's n = 3
# For each case:
#   T1      TukeyHSD(aov(len ~ supp * dose)) on the supp:dose term — cell means, interaction-model
#           error, df = N - 4. Every pair: diff and adjusted p.
#   T2      Tukey over cell means with the ADDITIVE model's error (df = N - 3). TukeyHSD cannot form
#           this, so it is computed here with ptukey from the additive aov's residual mean square.
#   T3      unadjusted pairwise t on the interaction-model error (Fisher's LSD), via pt.
#   T4, T5  t.test on the two cells of each pair, var.equal = TRUE and FALSE.
# Plus a ptukey grid (upper tail) for the distribution function itself.

out <- data.frame(case = character(), quantity = character(), pair = character(),
                  value = character(), stringsAsFactors = FALSE)
add <- function(case, quantity, pair, value) {
  shown <- if (is.na(value)) "" else trimws(formatC(as.numeric(value), digits = 17, format = "g"))
  out[nrow(out) + 1, ] <<- list(case, quantity, pair, shown)
}

tg <- ToothGrowth[ToothGrowth$dose %in% c(0.5, 1.0), ]
tg$dose <- factor(tg$dose)
tg$cell <- interaction(tg$supp, tg$dose, sep = ":")

cases <- list(
  tg_n10 = tg,
  tg_n3 = do.call(rbind, lapply(split(tg, tg$cell, drop = TRUE), function(d) d[1:3, ]))
)

for (name in names(cases)) {
  d <- cases[[name]]
  d$cell <- droplevels(d$cell)
  n <- nrow(d)
  full <- aov(len ~ supp * dose, data = d)
  additive <- aov(len ~ supp + dose, data = d)
  mse_full <- sum(residuals(full)^2) / (n - 4)
  mse_add <- sum(residuals(additive)^2) / (n - 3)
  per_cell <- n / 4
  add(name, "n", "", n)
  add(name, "mse_interaction", "", mse_full)
  add(name, "mse_additive", "", mse_add)

  hsd <- TukeyHSD(full, "supp:dose")[["supp:dose"]]
  means <- tapply(d$len, d$cell, mean)
  for (pair in rownames(hsd)) {
    cells <- strsplit(pair, "-")[[1]]
    diff <- means[[cells[1]]] - means[[cells[2]]]
    add(name, "diff", pair, hsd[pair, "diff"])
    add(name, "T1_p", pair, hsd[pair, "p adj"])
    add(name, "T2_p", pair,
        ptukey(abs(diff) / sqrt(mse_add / per_cell), 4, n - 3, lower.tail = FALSE))
    add(name, "T3_p", pair,
        2 * pt(abs(diff) / sqrt(2 * mse_full / per_cell), n - 4, lower.tail = FALSE))
    a <- d$len[d$cell == cells[1]]
    b <- d$len[d$cell == cells[2]]
    add(name, "T4_p", pair, t.test(a, b, var.equal = TRUE)$p.value)
    add(name, "T5_p", pair, t.test(a, b, var.equal = FALSE)$p.value)
  }
}

for (df in c(8, 9, 36, 37)) {
  for (q in c(0.5, 1, 2, 3, 3.5, 4, 5, 6, 8)) {
    add("ptukey_grid", "upper_tail", sprintf("q=%g;nmeans=4;df=%d", q, df),
        ptukey(q, 4, df, lower.tail = FALSE))
  }
}

add("environment", "R.version", R.version.string, NA)
dir.create("tests/fixtures", showWarnings = FALSE, recursive = TRUE)
write.csv(out, "tests/fixtures/r_tukey_reference.csv", row.names = FALSE)
cat(sprintf("wrote %d reference values to tests/fixtures/r_tukey_reference.csv under %s\n",
            nrow(out) - 1, R.version.string))
