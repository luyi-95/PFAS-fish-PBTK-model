library(deSolve)
library(openxlsx)
library(minpack.lm)

#========================================================
#  ========================================================
#Arrhenius temperature function
KT <- function(T, TR, TA) { exp((TA / TR) - (TA / T)) }

#========================================================
#(I) Simplified PBTK Model - corrected version
#========================================================
ZF.model.simple <- function(t, initial_v, phys_exp_parms, chem_parms) {
  with(as.list(phys_exp_parms), {
    
    #-----------------------------
    # unpack states
    #-----------------------------
    y_mat <- matrix(unname(initial_v), nrow = n)
    
    A_absorb_gill <- y_mat[, 1]
    A_excr_gill   <- y_mat[, 2]
    A_urine       <- y_mat[, 3]
    A_feces       <- y_mat[, 4]
    A_excr_water  <- y_mat[, 5]
    A_egg_cum     <- y_mat[, 6]
    A_GB          <- y_mat[, 7]
    A_blood       <- y_mat[, 8]
    A_liv         <- y_mat[, 9]
    A_gon         <- y_mat[, 10]
    A_git         <- y_mat[, 11]
    A_kidney      <- y_mat[, 12]
    A_fil         <- y_mat[, 13]
    A_rest        <- y_mat[, 14]
    A_water       <- y_mat[, 15]
    
    #-----------------------------
    # unpack chemical parameters
    #-----------------------------
    chem_mat <- matrix(unname(chem_parms), nrow = n)
    
    i             <- chem_mat[, 1]
    pKa           <- chem_mat[, 2]
    logKow        <- chem_mat[, 3]
    MW            <- chem_mat[, 4]
    pKd           <- chem_mat[, 5]
    Plivb         <- chem_mat[, 6]
    Pgonb         <- chem_mat[, 7]
    Pgitb         <- chem_mat[, 8]
    Prestb        <- chem_mat[, 9]
    Pkidb         <- chem_mat[, 10]
    KabsK         <- chem_mat[, 11]
    KeliL         <- chem_mat[, 12]
    Kegg          <- chem_mat[, 13]
    R_loss        <- chem_mat[, 14]
    WaterExposure <- chem_mat[, 15]
    
    #-----------------------------
    # volumes
    #-----------------------------
    V_blood  <- sc_blood  * BW
    V_liv    <- sc_liv    * BW
    V_GB     <- sc_GB     * BW
    V_gon    <- sc_gon    * BW
    V_git    <- sc_git    * BW
    V_kidney <- sc_kidney * BW
    V_fil    <- sc_fil    * BW
    V_rest   <- BW - (V_blood + V_liv + V_GB + V_gon + V_git + V_kidney + V_fil)
    
    if (V_rest <= 0) stop("V_rest <= 0; check volume scaling.")
    
    #-----------------------------
    # temperature & cardiac output
    #-----------------------------
    TC_k  <- TC_c + 273.15
    Fcard <- (F_card_ref * KT(T=TC_k, TR=TR_Fcard, TA=TA) * (BW/Bw_Fcard_ref)^(-0.1)) * BW
    
    #-----------------------------
    # blood flows
    #-----------------------------
    Fliv    <- liv_frac    * Fcard
    Fgon    <- gon_frac    * Fcard
    Fgit    <- git_frac    * Fcard
    Fkidney <- kidney_frac * Fcard
    Ffil    <- fil_frac    * Fcard
    Frest   <- Fcard - (Fliv + Fgon + Fgit + Fkidney + Ffil)
    
    #-----------------------------
    # ventilation
    #-----------------------------
    VO2     <- (VO2_ref * KT(T=TC_k, TR=TR_VO2, TA=TA) * (BW/BW_VO2_ref)^(-0.1)) * BW
    Co2w    <- ((-0.24 * TC_c + 14.04) * Sat) / 1e3
    y_water <- VO2 / (OEE * Co2w) * (1 / (1000^0.25 * BW^0.75))
    
    #-----------------------------
    # competitive protein binding
    #-----------------------------
    L0 <- A_blood
    P_avail_local <- P_avail
    PL <- rep(0, n)
    
    if (!all(L0 == 0)) {
      PL_old  <- PL
      Kdiss   <- 10.0^(-pKd)
      toler   <- 1e-4
      maxiter <- length(Kdiss) * 1000
      L0_mol  <- (L0 * 1e-6) / (MW * (V_blood * 1e-3))
      PL_new  <- rep(0, length(Kdiss))
      
      for (iter in seq_len(maxiter)) {
        P_tmp <- P_avail_local
        for (j in seq_along(Kdiss)) {
          b <- P_tmp + PL_old[j] + L0_mol[j] + Kdiss[j]
          c <- (P_tmp + PL_old[j]) * L0_mol[j]
          disc <- b*b - 4*c
          disc <- pmax(disc, 0)
          PL_new[j] <- (b - sqrt(disc)) / 2
          P_tmp <- P_tmp + PL_old[j] - PL_new[j]
        }
        tm <- sum(abs((PL_old - PL_new) / (PL_new + 1e-20)))
        if (tm < toler) break
        PL_old <- PL_new
      }
      PL <- PL_new
      P_avail_local <- P_tmp
    }
    
    blood_bound <- PL * MW * 1000 * V_blood
    fu <- rep(1, n)
    idx  <- A_blood > 0
    fu[idx] <- 1 - (blood_bound[idx] / A_blood[idx])
    fu <- pmax(0, pmin(1, fu))
    
    #-----------------------------
    # gill exchange parameters
    #-----------------------------
    logKow_ion <- logKow - delta_Kow
    fn_fish    <- 1 / (1 + 10^(i * (7.4 - pKa)))
    dow        <- fn_fish * 10^logKow + (1 - fn_fish) * 10^logKow_ion
    PBW        <- 0.008*0.3*dow + 0.007*2.0*dow^0.94 + 0.134*2.9*dow^0.63 + 0.851
    y_blood    <- Fcard * PBW * (1 / (1000^0.25 * BW^0.75))
    
    kx   <- ((BW/1000)^0.75) / (2.8e-3 + 68/dow + 1/y_water + 1/y_blood) * 1000
    kout <- (1 / (68*(dow-1) + 1)) * kx
    
    F_bile   <- 0.0022 * BW^0.75
    dV_urine <- urine_rate * BW^0.75
    
    #-----------------------------
    # cumulative tracking
    #-----------------------------
    dA_absorb_gill     <- kx       * (A_water / V_water)
    dA_excr_gill       <- kout     * (A_blood * fu / V_blood)
    dA_urine           <- dV_urine * (A_fil / V_fil)
    dA_feces           <- R_loss * F_bile * (A_GB / V_GB) 
    dA_excr_water_flux <- dA_excr_gill + dA_urine + dA_feces
    dA_egg_cum         <- Kegg * (A_gon / V_gon)
    
    #-----------------------------
    # ODE system
    #-----------------------------
    
    dA_rest <- fu * Frest * (A_blood/V_blood - (A_rest/V_rest)/Prestb)
    
    dA_blood <- dA_absorb_gill - dA_excr_gill -
      fu * (A_blood/V_blood) * (Fliv + Fgon + Fgit + Fkidney + Frest) -
      Ffil * fu * (A_blood/V_blood) +
      fu * (Frest   * ((A_rest/V_rest) / Prestb) +
              Fkidney * ((A_kidney/V_kidney) / Pkidb) +
              Fgon    * ((A_gon / V_gon) / Pgonb) +          
              (Fliv + Fgit) * ((A_liv / V_liv) / Plivb)      
      )
    
    dA_liv <- fu * ( Fliv * (A_blood / V_blood) +
                       Fgit * ((A_git / V_git) / Pgitb) -
                       (Fliv + Fgit) * ((A_liv / V_liv) / Plivb) ) - 
                         (KeliL + F_bile)* (A_liv / V_liv)
    
    dA_gon  <- fu * Fgon * (A_blood/V_blood - (A_gon/V_gon)/Pgonb) - (Kegg * (A_gon / V_gon))
    
    dA_GB <- (KeliL + F_bile)* (A_liv / V_liv) - F_bile * (A_GB / V_GB)
    
    dA_git <- fu * Fgit * ((A_blood/V_blood) - (A_git/V_git)/Pgitb) +
      (1-R_loss)* F_bile * (A_GB / V_GB) 
    
    dA_kidney <- fu * Fkidney * (A_blood/V_blood - (A_kidney/V_kidney)/Pkidb) + (KabsK * (A_fil / V_fil))
    
    dA_fil <- Ffil * fu * (A_blood/V_blood) - (KabsK * (A_fil / V_fil)) - dA_urine
    
    dA_water <- dA_excr_water_flux - dA_absorb_gill
    
    A_body <- A_blood + A_liv + A_GB + A_gon + A_git + A_kidney + A_fil + A_rest
    
    A_elim <- A_excr_water + A_egg_cum
    
    Mass_total <- A_water + A_body + A_egg_cum
    
    C_whole_body <- A_body / BW
    C_blood   <- A_blood  / V_blood
    C_plasma  <- A_blood  / V_blood * (1 - fu) / 0.45
    C_liv     <- A_liv    / V_liv
    C_GB      <- A_GB     / V_GB
    C_gon     <- A_gon    / V_gon
    C_git     <- A_git    / V_git
    C_kidney  <- A_kidney / V_kidney
    C_fil     <- A_fil    / V_fil
    C_rest    <- A_rest   / V_rest
    
    list(
      c(
        dA_absorb_gill, dA_excr_gill, dA_urine, dA_feces,
        dA_excr_water_flux, dA_egg_cum,
        dA_GB, dA_blood, dA_liv, dA_gon,
        dA_git, dA_kidney, dA_fil, dA_rest, dA_water
      ),
      Mass_total   = Mass_total,
      P_avail      = P_avail_local * 1e6,
      fu         = fu,
      C_whole_body = C_whole_body,
      C_blood      = C_blood,
      C_liv        = C_liv,
      C_GB         = C_GB,
      C_gon        = C_gon,
      C_git        = C_git,
      C_kidney     = C_kidney,
      C_fil        = C_fil,
      C_rest       = C_rest,
      C_plasma     = C_plasma,
      A_elim       = A_elim
    )
  })
}

#========================================================
#(II) Parameters
#========================================================
phys_parms <- c(
  Bw_Fcard_ref = 0.5, BW_VO2_ref = 0.4,
  TA = 3000, TR_Fcard = 299.5, TR_VO2 = 300.15,
  V_water = 1E12, F_card_ref = 41.328, VO2_ref = 9.84,
  OEE = 0.71, Sat = 0.90,
  
  #Organ volume scaling
  sc_blood = 0.0222, sc_gon = 0.05, sc_liv = 0.036,
  sc_GB = 0.003, sc_git = 0.051, sc_kidney = 0.002,
  sc_fil = 0.0002,
  #
  #Fractional blood flows
  gon_frac = 0.01252, liv_frac = 0.01942,
  git_frac = 0.174, kidney_frac = 0.01,
  fil_frac = 0.005,
  
  P_avail = 0.0006,
  delta_Kow = 3.1,
  urine_rate = 0.073
)

chem_parms <- c(
  i = c( 1, 1, 1, 1),
  pKa = c(-3.27, -3.34, 0.5, -3.57),
  logKow = c( 6.05, 5.05, 5.0, 4.2),
  MW     = c(500.13, 400.12, 414.07, 300.1),
  pKd    = c( 4.20, 3.15, 3.08, 2.98),
  Plivb  = c( 0.88, 0.85, 0.74, 0.71),
  Pgonb  = c( 0.35, 0.18, 0.17, 0.13),
  Pgitb  = c( 0.93, 0.90, 0.90, 0.85),
  Prestb = c( 0.55, 0.53, 0.46, 0.27),
  Pkidb  = c( 0.45, 0.34, 0.34, 0.60),
  KabsK = c( 2.24, 1.71, 1.47, 0.15),
  KeliL = c( 0.003, 0.002, 0.002, 0.001),
  Kegg  = c( 0.20, 0.20, 0.20, 0.20),
  R_loss = c( 0.02, 0.02, 0.02, 0.02),
  WaterExposure = c(7.8e-3, 8.7e-3, 8.6e-3, 9.5e-3) # mg/L
)

#========================================================
#(III) Initial States & Simulation Setup
#========================================================
n <- 4

Cw_vec <- unname(chem_parms[grepl("WaterExposure", names(chem_parms))])

yini <- c(
  A_absorb_gill = rep(0, n), A_excr_gill = rep(0, n),
  A_urine = rep(0, n), A_feces = rep(0, n),
  A_excr_water = rep(0, n), A_egg_cum = rep(0, n),
  A_GB = rep(0, n), A_blood = rep(0, n),
  A_liv = rep(0, n), A_gon = rep(0, n),
  A_git = rep(0, n), A_kidney = rep(0, n),
  A_fil = rep(0, n), A_rest = rep(0, n),
  A_water = Cw_vec * unname(phys_parms["V_water"])
)
water_exp_event <- if (n > 1) paste0("A_water", seq_len(n)) else "A_water"

exposure_parms <- c(
  Times <- seq(0, 21),
  TC_c = 26,
  BW = 0.6,
  time_first_dose = 0,
  time_end_exposure = 14
)

events <- list(data = data.frame(
  var = water_exp_event, time = as.numeric(exposure_parms["time_end_exposure"]),
  value = 0, method = "replace"
))

phys_exp_parms <- c(phys_parms, exposure_parms, n = n)

#========================================================
#(IV) Run Simulation
#========================================================
out <- ode(
  times = Times,
  func = ZF.model.simple,
  y = yini,
  parms = phys_exp_parms,
  chem_parms = chem_parms,
  method = "lsodes",
  events = events
)
out_df <- as.data.frame(out)
specific_times <- c(1, 3, 5, 7, 10, 12, 14, 15, 18, 21)
specific_data <- out_df[out_df$time %in% specific_times, ]
View (specific_data)

#===============================================
# (III) Fitting ku and ke (修正版)
#===============================================

fit_ku_ke <- function(time, conc, Cw, te){
  df <- data.frame(t = time, C = conc)
  dep <- subset(df, t > te & C > 0)
  
  # 预设返回全是 NA 的结果，防止后续报错
  res_na <- c(ku=NA_real_, ke=NA_real_, logBCF=NA_real_, T_half=NA_real_)
  
  # Safety check for sufficient data points
  if(nrow(dep) < 3) {
    return(res_na)
  }
  
  # Estimate initials
  
  ke0 <- tryCatch({
    max(1e-6, -coef(lm(log(C) ~ I(t - te), dep))[2])
  }, error = function(e) 0.1)
  
  # Cw is scalar here
  max_C <- max(df$C, na.rm=TRUE)
  if(is.infinite(max_C) | is.na(max_C)) max_C <- 0
  
  ku0 <- max(1e-8, ke0 * max_C / Cw * 0.8)
  
  # Find C00 safely
  idx_min <- which.min(abs(df$t - 0))
  if(length(idx_min) == 0) C00 <- 0 else C00 <- max(0, df$C[idx_min], na.rm=TRUE)
  
  fit <- tryCatch({
    nlsLM(
      C ~ ifelse(t <= te,
                 C0*exp(-ke*t) + (ku*Cw/ke)*(1 - exp(-ke*t)),
                 (C0*exp(-ke*te) + (ku*Cw/ke)*(1 - exp(-ke*te))) * exp(-ke*(t - te))),
      data = df,
      start = list(ku=ku0, ke=ke0, C0=C00),
      lower = c(0, 1e-8, 0), upper = c(Inf, Inf, Inf),
      control = nls.lm.control(maxiter = 200)
    )
  }, error = function(e) return(NULL))
  
  if(!is.null(fit)){
    co <- coef(fit)
    # as.numeric 去掉可能存在的名称属性
    ku <- as.numeric(co["ku"])
    ke <- as.numeric(co["ke"])
    t12 <- log(2)/ke
    logBCF <- log10(ku/ke)
    return(c(ku=ku, ke=ke, logBCF=logBCF, T_half=t12))
  } else {
    return(res_na)
  }
}

estimate_all <- function(out_df, pfas_names, Cw_vec, te){
  res <- lapply(seq_along(pfas_names), function(i){
    # Ensure column naming matches deSolve output
    col <- paste0("C_whole_body", i) 
    if(!col %in% names(out_df)) {
      # Fallback if n=1 (no index)
      if(length(pfas_names)==1) col <- "C_whole_body" 
    }
    
    # 运行拟合
    pars <- fit_ku_ke(out_df$time, out_df[[col]], Cw_vec[i], te)
    
    data.frame(
      PFAS   = pfas_names[i],
      ku     = as.numeric(pars["ku"]),
      ke     = as.numeric(pars["ke"]),
      logBCF = as.numeric(pars["logBCF"]),
      T_half = as.numeric(pars["T_half"]),
      stringsAsFactors = FALSE
    )
  })
  
  # 现在 rbind 应该可以正常工作了
  do.call(rbind, res)
}

# Run Estimation
# 确保 pfas_names 在这里被定义
pfas_names <- c("PFOS", "PFHxS", "PFOA", "PFBS") 

te     <- as.numeric(phys_exp_parms["time_end_exposure"])
Cw_vec <- unname(chem_parms[grepl("WaterExposure", names(chem_parms))])

res <- estimate_all(out_df, pfas_names, Cw_vec, te)
print(res)
#1