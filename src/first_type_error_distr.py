from src.stattests_paper import *
from scipy.stats import chi2

NUMBER_OF_SNPS = 2
POPULATION_SIZE = 10000  # 100000
REF_POPULATION_SIZE = 10000  # 100000

FREQ_A1 = 0.6
FREQ_B1 = 0.5
# FREQ_B1 = 0.6

REF_FREQ_A1 = 0.6
REF_FREQ_B1 = 0.5
# REF_FREQ_B1 = 0.6

R_PAR = [0.7]
# R_PAR = [0.3, 0.4, 0.5, 0.6, 0.7]
# NEG_R_PAR = [element * -1 for element in R_PAR]
# D = R * np.sqrt(FREQ_A1 * (1 - FREQ_A1) * FREQ_B1 * (1 - FREQ_B1))

# REF_R = 0.5
COEFF_R_D = np.sqrt(REF_FREQ_A1 * (1 - REF_FREQ_A1) * REF_FREQ_B1 * (1 - REF_FREQ_B1))
# REF_D = REF_R * COEFF_R_D
# Restrictions on D: -min(P_A * P_B, P_a * P_b) <= D <= min(P_A * P_b, P_a * P_B)

BETA_A = 10/np.sqrt(POPULATION_SIZE)  # 0.03
BETA_B = 0.0  # -0.01
print("BETA_A:", BETA_A)

P_VALUE_THRESHOLD = 0.1
NUMBER_OF_ITERATIONS = 1000


def main():

    results = {"sim_r": [], "ref_r": [], "joint_p": [], "real_r": [], "joint_p_1": [], "joint_p_2": []}

    for R in R_PAR:
        print("\tr =", R)
        D = R * np.sqrt(FREQ_A1 * (1 - FREQ_A1) * FREQ_B1 * (1 - FREQ_B1))
        for i in range(NUMBER_OF_ITERATIONS):
            if i % 100 == 0:
                print("\t\ti =", i + 1)

            haplotypes_prob = get_haplotypes_probabilities(D, FREQ_A1, FREQ_B1)
            haplotypes = get_haplotypes(haplotypes_prob, POPULATION_SIZE)
            genotypes = get_genotypes(haplotypes, POPULATION_SIZE)
            genotypes_std = standardise_genotypes(genotypes, FREQ_A1, FREQ_B1)
            phenotypes = get_phenotypes(genotypes_std, BETA_A, BETA_B, POPULATION_SIZE)

            simulated_data = pd.DataFrame({"phenotype": phenotypes,
                                           "snp_a_gen": genotypes_std[:, 0],
                                           "snp_b_gen": genotypes_std[:, 1]})

            # model = smf.ols('phenotype ~ snp_a_gen + snp_b_gen', data=simulated_data).fit()

            gwas = get_gwas(simulated_data,
                            freq_a1=1 - sum(genotypes[:, 0]) / (2 * POPULATION_SIZE),
                            freq_b1=1 - sum(genotypes[:, 1]) / (2 * POPULATION_SIZE))

            n_points = 50
            r_real = round(np.corrcoef(genotypes[:, 0], genotypes[:, 1])[0, 1], 3)

            #for ref_r in np.linspace(-1.0, 1.0, n_points):
            for ref_r in [r_real]:
                ref_r = round(ref_r, 3)
                try:
                    joint_beta, joint_se, joint_p = joint_test(gwas=gwas,
                                                               population_size=POPULATION_SIZE,
                                                               ref_population_size=REF_POPULATION_SIZE,
                                                               ref_r=ref_r)
                    print(gwas, joint_beta, joint_se)
                    results["sim_r"].append(R)
                    results["ref_r"].append(ref_r)
                    results["joint_p"].append(joint_p)
                    results["real_r"].append(r_real)
                    results["joint_p_1"].append(chi2.sf((joint_beta[0, 0]/joint_se[0])**2, 1))
                    results["joint_p_2"].append(chi2.sf((joint_beta[0, 1]/joint_se[1])**2, 1))

                except np.linalg.linalg.LinAlgError:
                    pass

            """
            for ref_r in r_iter:
                # print("REF_R =", ref_r)
                try:
                    joint_beta, joint_se, joint_p = joint_test(gwas=gwas,
                                                               population_size=POPULATION_SIZE,
                                                               ref_population_size=REF_POPULATION_SIZE,
                                                               ref_r=ref_r)
                    results["ref_r"].append(ref_r)
                    results["joint_p"].append(joint_p)
                    results["real_r"].append(r_real)
    
                except np.linalg.linalg.LinAlgError:
                    pass
            """

        first_type_error = pd.DataFrame.from_dict(results)
        first_type_error["delta_r"] = first_type_error["sim_r"] - first_type_error["ref_r"]
        first_type_error.to_csv("../out/first_type_error_b.tsv", sep='\t', header=True, index=False)

    """
    print("Multiple regression \n second type error =",
          sum(distr_p_value.pJ_multiple > 0.05) / POPULATION_SIZE * 100,
          "\n error of error =",
          np.sqrt(sum(distr_p_value.pJ_multiple <= 0.05) * sum(results.pJ_multiple > 0.05)) / POPULATION_SIZE)
    print("Implemented algorithm \n second type error =",
          sum(distr_p_value.pJ_sim > 0.05) / POPULATION_SIZE * 100,
          "\n error of error =",
          np.sqrt(sum(distr_p_value.pJ_sim <= 0.05) * sum(distr_p_value.pJ_sim > 0.05)) / POPULATION_SIZE)

    """


if __name__ == "__main__":
    main()
