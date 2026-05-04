library(deSolve)
library(minpack.lm) # 仅用于最终结果验证，不再参与主优化循环

# ========================================================
# Arrhenius 方程
# ========================================================
KT <- function(T, TR, TA) { exp((TA / TR) - (TA / T)) }

# ========================================================
# PBTK Model（保持原始核心逻辑，未作侵入式修改）
# ========================================================
ZF.model.simple <- function(t, initial_v, phys_exp_parms, chem_parms) {
  with(as.list(phys_exp_parms), {
    y <- unname(initial_v)
    V_urine <- y[1]
    k <- 0
    A_absorb_gill <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_excr_gill   <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_urine       <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_feces       <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_excr_water  <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_egg_cum     <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_GB          <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_blood       <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_liv         <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_gon         <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_git         <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_kidney      <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_fil         <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_rest        <- y[(2+n*k):((2+n-1)+n*k)]; k <- k+1
    A_water       <- y[(2+n*k):((2+n-1)+n*k)]
    
    chem_p <- unname(chem_parms)
    k <- 0
    i             <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    pKa           <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    logKow        <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    MW            <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    pKd           <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Plivb         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Pgonb         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Pgitb         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Prestb        <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Pkidb         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    KabsK         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    KeliL         <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    Kegg          <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    R_loss        <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    PL            <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    blood_bound   <- chem_p[(1+n*k):((1+n-1)+n*k)]; k <- k+1
    WaterExposure <- chem_p[(1+n*k):((1+n-1)+n*k)]
    
    V_blood  <- sc_blood  * BW^0.75
    V_liv    <- sc_liv    * BW^0.75
    V_GB     <- sc_GB     * BW^0.75
    V_gon    <- sc_gon    * BW^0.75
    V_git    <- sc_git    * BW^0.75
    V_kidney <- sc_kidney * BW^0.75
    V_fil    <- sc_fil    * BW^0.75
    V_rest   <- BW - (V_blood + V_liv + V_GB + V_gon + V_git + V_kidney + V_fil)
    if (V_rest <= 0) stop("V_rest <= 0")
    
    TC_k  <- TC_c + 273.15
    Fcard <- (F_card_ref * KT(T=TC_k, TR=TR_Fcard, TA=TA) * (BW/Bw_Fcard_ref)^(-0.1)) * BW
    
    Fliv    <- liv_frac    * Fcard
    Fgon    <- gon_frac    * Fcard
    Fgit    <- git_frac    * Fcard
    Fkidney <- kidney_frac * Fcard
    Ffil    <- fil_frac    * Fcard
    Frest   <- Fcard - (Fliv + Fgon + Fgit + Fkidney + Ffil)
    
    VO2     <- (VO2_ref * KT(T=TC_k, TR=TR_VO2, TA=TA) * (BW/BW_VO2_ref)^(-0.1)) * BW
    Co2w    <- ((-0.24 * TC_c + 14.04) * Sat) / 1e3
    y_water <- VO2 / (OEE * Co2w) * (1 / (1000^0.25 * BW^0.75))
    
    # 竞争蛋白结合模块 (n=1 时保持原样计算以确保一致性)
    L0 <- A_blood
    P_avail_local <- P_avail
    if (!all(L0 == 0)) {
      PL_old <- PL; Kdiss <- 10^(-pKd)
      toler <- 1e-4; maxiter <- length(Kdiss) * 1000
      L0_mol <- (L0 * 1e-6) / (MW * (V_blood * 1e-3))
      PL_new <- rep(0, length(Kdiss))
      for (iter in seq_len(maxiter)) {
        P_tmp <- P_avail_local
        for (j in seq_along(Kdiss)) {
          b <- P_tmp + PL_old[j] + L0_mol[j] + Kdiss[j]
          c <- (P_tmp + PL_old[j]) * L0_mol[j]
          PL_new[j] <- (b - sqrt(pmax(b*b - 4*c, 0))) / 2
          P_tmp <- P_tmp + PL_old[j] - PL_new[j]
        }
        if (sum(abs((PL_old - PL_new) / (PL_new + 1e-20))) < toler) break
        PL_old <- PL_new
      }
      PL <- PL_new; P_avail_local <- P_tmp
    }
    blood_bound <- PL * MW * 1000 * V_blood
    free <- rep(1, n)
    idx  <- A_blood > 0
    free[idx] <- 1 - (blood_bound[idx] / A_blood[idx])
    free <- pmax(0, pmin(1, free))
    
    logKow_ion <- logKow - delta_Kow
    fn_fish    <- 1 / (1 + 10^(i * (7.4 - pKa)))
    dow        <- fn_fish * 10^logKow + (1 - fn_fish) * 10^logKow_ion
    PBW        <- 0.008*0.3*dow + 0.007*2.0*dow^0.94 + 0.134*2.9*dow^0.63 + 0.851
    y_blood    <- Fcard * PBW * (1 / (1000^0.25 * BW^0.75))
    kx   <- ((BW/1000)^0.75) / (2.8e-3 + 68/dow + 1/y_water + 1/y_blood) * 1000
    kout <- (1 / (68*(dow-1) + 1)) * kx
    
    F_bile   <- 0.0022 * BW^0.75
    dV_urine <- urine_rate * BW^0.75
    
    Flux_absK <- KabsK * (A_fil / V_fil)
    Flux_eliL <- KeliL * (A_liv / V_liv)
    Flux_egg  <- Kegg  * (A_gon / V_gon)
    Flux_bile <- F_bile * (A_liv / V_liv)
    
    dA_absorb_gill     <- kx   * (A_water / V_water)
    dA_excr_gill       <- kout * (A_blood * free / V_blood)
    dA_urine           <- dV_urine * (A_fil / V_fil)
    dA_feces           <- R_loss * F_bile * (A_GB / V_GB)
    dA_excr_water_flux <- dA_excr_gill + dA_urine + dA_feces
    dA_egg_cum         <- Flux_egg
    
    dA_rest <- free * Frest * (A_blood/V_blood - (A_rest/V_rest)/Prestb)
    dA_liv  <- free * (Fliv*(A_blood/V_blood) +
                         Fgit*((A_git/V_git)/Pgitb) -
                         (Fliv+Fgit)*((A_liv/V_liv)/Plivb)) - Flux_eliL - Flux_bile
    dA_blood <- dA_absorb_gill - dA_excr_gill -
      free*(A_blood/V_blood)*(Fliv+Fgon+Fgit+Fkidney+Frest) -
      Ffil*free*(A_blood/V_blood) +
      free*(Frest*((A_rest/V_rest)/Prestb) +
              Fkidney*((A_kidney/V_kidney)/Pkidb) +
              Fgon*((A_gon/V_gon)/Pgonb) +
              (Fliv+Fgit)*((A_liv/V_liv)/Plivb))
    dA_gon    <- free*Fgon*(A_blood/V_blood - (A_gon/V_gon)/Pgonb) - Flux_egg
    dA_GB     <- Flux_bile + Flux_eliL - F_bile*(A_GB/V_GB)
    dA_git    <- free*Fgit*((A_blood/V_blood) - (A_git/V_git)/Pgitb) +
      (1-R_loss)*F_bile*(A_GB/V_GB)
    dA_kidney <- free*Fkidney*(A_blood/V_blood - (A_kidney/V_kidney)/Pkidb) + Flux_absK
    dA_fil    <- Ffil*free*(A_blood/V_blood) - Flux_absK - dA_urine
    dA_water  <- dA_excr_water_flux - dA_absorb_gill
    
    list(c(dV_urine,
           dA_absorb_gill, dA_excr_gill, dA_urine, dA_feces,
           dA_excr_water_flux, dA_egg_cum,
           dA_GB, dA_blood, dA_liv, dA_gon,
           dA_git, dA_kidney, dA_fil, dA_rest, dA_water))
  })
}

# ========================================================
# 物理与暴露参数
# ========================================================
phys_parms <- c(
  Bw_Fcard_ref=0.5, BW_VO2_ref=0.4,
  TA=3000, TR_Fcard=299.5, TR_VO2=300.15,
  V_water=1E12, F_card_ref=41.328, VO2_ref=9.84,
  OEE=0.71, Sat=0.90,
  sc_blood=0.0222, sc_gon=0.05,   sc_liv=0.02,
  sc_GB=0.0012,    sc_git=0.051,  sc_kidney=0.002,
  sc_fil=0.0002,
  gon_frac=0.01252, liv_frac=0.01942,
  git_frac=0.174,   kidney_frac=0.01,
  fil_frac=0.005,
  P_avail=0.0006, delta_Kow=3.1, urine_rate=0.073
)

exposure_parms <- c(TC_c=26, BW=0.8,
                    time_first_dose=0, time_end_exposure=24)

chem_matrix <- list(
  i      = c(    1,       1,      1,     1),
  pKa    = c(-3.27,   -3.34,    0.5, -3.57),
  logKow = c( 6.15,    5.15,    5.0,   3.9),
  MW     = c(500.13, 400.12, 414.07, 300.1),
  pKd    = c(  4.20,   3.15,   3.08,  2.98),
  Plivb  = c(  0.88,   0.85,   0.74,  1.71),
  Pgonb  = c(  0.55,   0.32,   0.40,  0.19),
  Pgitb  = c(  0.93,   0.90,   0.90,  0.85),
  Prestb = c(  0.35,   0.13,   0.26,  0.27),
  Pkidb  = c(  0.35,   0.64,   0.64,  0.70),
  KabsK  = c(  2.24,   1.71,   0.47,  0.05),  
  KeliL  = c(  2.40,   1.90,   1.98,  0.20),
  Kegg   = c(  0.20,   0.20,   0.20,  0.20),
  R_loss = c(  0.022,  0.022,  0.022, 0.022),
  PL           = c(0, 0, 0, 0),
  blood_bound  = c(0, 0, 0, 0),
  WaterExposure= c(10.2e-3, 15.2e-3, 6.64e-3, 10.8e-3)
)
pfas_names <- c("PFOS", "PFHxS", "PFOA", "PFBS")

target <- data.frame(
  PFAS   = pfas_names,
  ku     = c(47.2275207,  7.2026898, 5.0947259, 0.9430869),
  ke     = c( 0.05610236, 0.08613818, 0.09898718, 0.20837660),
  stringsAsFactors = FALSE
)

# ========================================================
# 辅助函数定义
# ========================================================
make_chem_parms_single <- function(chem_matrix, idx, KabsK_val) {
  c(
    i            = chem_matrix$i[idx],
    pKa          = chem_matrix$pKa[idx],
    logKow       = chem_matrix$logKow[idx],
    MW           = chem_matrix$MW[idx],
    pKd          = chem_matrix$pKd[idx],
    Plivb        = chem_matrix$Plivb[idx],
    Pgonb        = chem_matrix$Pgonb[idx],
    Pgitb        = chem_matrix$Pgitb[idx],
    Prestb       = chem_matrix$Prestb[idx],
    Pkidb        = chem_matrix$Pkidb[idx],
    KabsK        = KabsK_val,
    KeliL        = chem_matrix$KeliL[idx],
    Kegg         = chem_matrix$Kegg[idx],
    R_loss       = chem_matrix$R_loss[idx],
    PL           = 0,
    blood_bound  = 0,
    WaterExposure= chem_matrix$WaterExposure[idx]
  )
}

run_single <- function(KabsK_val, chem_matrix, compound_idx,
                       phys_parms, exposure_parms,
                       Times = seq(0, 48, by = 0.5)) {
  n_loc <- 1L
  phys_exp <- c(phys_parms, exposure_parms, n = n_loc)
  cp   <- make_chem_parms_single(chem_matrix, compound_idx, KabsK_val)
  Cw   <- cp["WaterExposure"]
  Vw   <- phys_parms["V_water"]
  te   <- exposure_parms["time_end_exposure"]
  
  yini <- c(V_urine=0, A_absorb_gill=0, A_excr_gill=0,
            A_urine=0, A_feces=0, A_excr_water=0, A_egg_cum=0,
            A_GB=0, A_blood=0, A_liv=0, A_gon=0,
            A_git=0, A_kidney=0, A_fil=0, A_rest=0,
            A_water = unname(Cw * Vw))
  
  events <- list(data = data.frame(
    var="A_water", time=as.numeric(te), value=0, method="replace"))
  
  # 修正：使用自适应 lsoda 替代强制刚性 lsodes，提高收敛性与速度
  out <- tryCatch(
    suppressWarnings(
      ode(times=Times, func=ZF.model.simple, y=yini,
          parms=phys_exp, chem_parms=cp,
          method="lsoda", events=events)
    ),
    error = function(e) NULL
  )
  if (is.null(out)) return(NULL)
  as.data.frame(out)
}

# 解析解：生成基准浓度曲线（消除模拟过程中的 NLS 嵌套需求）
generate_target_curve <- function(Times, ku, ke, Cw, te) {
  C_target <- numeric(length(Times))
  for (i in seq_along(Times)) {
    t <- Times[i]
    if (t <= te) {
      C_target[i] <- (ku * Cw / ke) * (1 - exp(-ke * t))
    } else {
      C_te <- (ku * Cw / ke) * (1 - exp(-ke * te))
      C_target[i] <- C_te * exp(-ke * (t - te))
    }
  }
  return(C_target)
}

# NLS拟合仅用于最终验证报告，不再用于寻优循环
fit_ku_ke_from_curve <- function(out_df, Cw, te, V_blood) {
  if (!"A_blood" %in% names(out_df)) return(c(ku=NA, ke=NA))
  conc <- out_df$A_blood / V_blood
  time <- out_df$time
  df   <- data.frame(t=time, C=conc)
  
  dep  <- subset(df, t > te & C > 0)
  if (nrow(dep) < 3) return(c(ku=NA, ke=NA))
  
  ke0 <- tryCatch(
    max(1e-6, -coef(lm(log(C) ~ I(t-te), dep))[2]),
    error = function(e) 0.1)
  maxC <- max(df$C, na.rm=TRUE)
  ku0  <- max(1e-8, ke0 * maxC / Cw * 0.8)
  C00  <- max(0, df$C[which.min(abs(df$t))], na.rm=TRUE)
  
  fit <- tryCatch(
    nlsLM(C ~ ifelse(t <= te,
                     C0*exp(-ke*t) + (ku*Cw/ke)*(1-exp(-ke*t)),
                     (C0*exp(-ke*te) + (ku*Cw/ke)*(1-exp(-ke*te)))*exp(-ke*(t-te))),
          data=df, start=list(ku=ku0, ke=ke0, C0=C00),
          lower=c(0, 1e-8, 0), upper=c(Inf, Inf, Inf),
          control=nls.lm.control(maxiter=200)),
    error = function(e) NULL)
  
  if (is.null(fit)) return(c(ku=NA, ke=NA))
  co <- coef(fit)
  c(ku=as.numeric(co["ku"]), ke=as.numeric(co["ke"]))
}

# ========================================================
# 主函数：解析解 Curve-Matching 寻优策略
# ========================================================
Times_sim <- seq(0, 48, by = 0.5)
te        <- as.numeric(exposure_parms["time_end_exposure"])
V_blood   <- phys_parms["sc_blood"] * exposure_parms["BW"]^0.75

results <- vector("list", length(pfas_names))

for (idx in seq_along(pfas_names)) {
  nm    <- pfas_names[idx]
  ku_t  <- target$ku[idx]
  ke_t  <- target$ke[idx]
  Cw_i  <- chem_matrix$WaterExposure[idx]
  
  cat(sprintf("\n[%s] 开始优化 KabsK ...\n", nm))
  
  # 预先生成目标的单室解析曲线
  target_curve <- generate_target_curve(Times_sim, ku_t, ke_t, Cw_i, te)
  
  # 目标函数：基于浓度的 Log-SSE (对数残差平方和)
  obj_curve_match <- function(log_K) {
    K <- exp(log_K)
    out_df <- run_single(K, chem_matrix, idx,
                         phys_parms, exposure_parms, Times_sim)
    
    # 惩罚项：求解失败
    if (is.null(out_df)) return(1e9) 
    
    C_sim <- out_df$A_blood / V_blood
    
    # 添加极小值平滑以避免 log(0)，稳健评估吸收与消除段特征
    eps <- 1e-9
    sse <- sum((log(C_sim + eps) - log(target_curve + eps))^2)
    return(sse)
  }
  
  # 粗略扫描区间（保持稳定）
  grid_log <- seq(log(1e-4), log(300), length.out = 30)
  grid_val <- sapply(grid_log, function(x) tryCatch(obj_curve_match(x), error=function(e) 1e9))
  best_i   <- which.min(grid_val)
  
  lo <- grid_log[max(1, best_i-2)]
  hi <- grid_log[min(length(grid_log), best_i+2)]
  
  # 精细优化
  opt <- tryCatch(
    optimize(obj_curve_match, interval = c(lo, hi), tol = 1e-6),
    error = function(e) list(minimum = grid_log[best_i], objective = grid_val[best_i])
  )
  
  KabsK_fit <- exp(opt$minimum)
  cat(sprintf("[%s] 寻优完毕: KabsK = %.6f (Log-SSE = %.6f)\n",
              nm, KabsK_fit, opt$objective))
  
  results[[idx]] <- list(PFAS=nm, KabsK=KabsK_fit, obj_val=opt$objective)
}

# ========================================================
# 汇总并验证（在此阶段运行一次 nlsLM 进行参数验算）
# ========================================================
cat("\n\n========== 反推结果汇总 ==========\n")
summary_df <- do.call(rbind, lapply(results, function(r) {
  idx    <- which(pfas_names == r$PFAS)
  Cw_i   <- chem_matrix$WaterExposure[idx]
  out_df <- run_single(r$KabsK, chem_matrix, idx,
                       phys_parms, exposure_parms, Times_sim)
  
  # 最终验证：仅在最优解处进行单次拟合
  pars   <- if (!is.null(out_df)) {
    fit_ku_ke_from_curve(out_df, Cw_i, te, V_blood)
  } else {
    c(ku=NA, ke=NA)
  }
  
  data.frame(
    PFAS         = r$PFAS,
    KabsK_fitted = round(r$KabsK, 6),
    ku_sim       = round(pars["ku"],    6),
    ku_target    = target$ku[idx],
    ke_sim       = round(pars["ke"],    8),
    ke_target    = target$ke[idx],
    logBCF_sim   = round(log10(pars["ku"]/pars["ke"]), 4),
    logBCF_target= round(log10(target$ku[idx]/target$ke[idx]), 4),
    stringsAsFactors = FALSE
  )
}))
rownames(summary_df) <- NULL
print(summary_df)