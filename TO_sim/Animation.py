from IPython.display import HTML
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from TO_sim.Utility import Check_PM_idx_omega
from TO_sim.Check_theoretical import Check_min_omega

def Animation_logabs(Ksdf, Ksrdf, N, m, MaxFrame=10000):
    fig = plt.figure(facecolor="white")
    ax11 = plt.subplot(221)
    ax12 = plt.subplot(222)
    ax22 = plt.subplot(212)
    logabs = lambda x: np.log(np.abs(x))

    def Slicing(x):
        slice_ = Ksdf["dtheta_s"].iloc[0].shape[0] // MaxFrame
        slice_ = 1 if slice_ <= 1 else slice_
        return x[::slice_, :]

    Temp_Ks = Ksdf["dtheta_s"].apply(logabs).apply(Slicing)
    Temp_Ksr = Ksrdf["dtheta_s"].apply(logabs).apply(Slicing)
    Ks = Ksdf.index
    Temp_rs = Ksdf["rs"]
    Temp_rsr = Ksrdf["rs"]
    Temp_t = Ksdf["ts"].iloc[0]
    t_end = Ksdf["ts"].iloc[0][-1]
    Ks = Ksdf.index
    K = Ks[0]

    ax11.clear()
    ax12.clear()
    ax11.set_xlabel(f"Oscillator No.(N={N})", fontsize=12)
    ax12.set_xlabel(f"Oscillator No.(N={N})", fontsize=12)
    ax11.set_title(f"Forward", fontsize=12)
    ax12.set_title(f"Backward", fontsize=12)
    ax12.tick_params(labelleft=False)
    ax11.set_ylabel("phase velocity\n" + r"($\log{|\dot{\theta}|}$)", fontsize=12)
    im11 = ax11.imshow(
        Temp_Ks[K], extent=[0, N, t_end, 0], aspect="auto", vmin=-8, vmax=3.4
    )
    im12 = ax12.imshow(
        Temp_Ksr[K], extent=[0, N, t_end, 0], aspect="auto", vmin=-8, vmax=3.4
    )
    # ax11.text(0,-5,f"m = {m}, K = {K}",fontsize=15)

    ax22.clear()
    ax22.plot(Temp_t, Temp_rs[K], label="Forward")
    ax22.plot(Temp_t, Temp_rsr[K], label="Backward")
    ax22.set_xlabel("Time[s]", fontsize=12)
    ax22.set_ylabel("Order\nparameter(r)", fontsize=12)
    ax22.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.20),
        fancybox=True,
        shadow=True,
        ncol=2,
    )
    ax22.set_ylim(0, 1)
    ax22.grid()
    divider11 = make_axes_locatable(ax11)
    divider12 = make_axes_locatable(ax12)
    cax11 = divider11.append_axes("right", size="5%", pad=0.05)
    cax12 = divider12.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im11, cax=cax11, orientation="vertical", extend="both")
    fig.colorbar(im12, cax=cax12, orientation="vertical", extend="both")
    fig.suptitle(f"m = {m}, K = {K}", fontsize=15, position=(0.5, 0.92))

    # fig.colorbar(pcm, ax = [ax11,ax12],location='bottom')

    # ax2.text(0,-5,f"K = {K}",fontsize=15)
    fig.tight_layout()

    def Update(K):
        ax11.clear()
        ax12.clear()
        ax11.set_title(f"Forward", fontsize=12)
        ax12.set_title(f"Backward", fontsize=12)
        ax11.set_xlabel(f"Oscillator No.(N={N})", fontsize=12)
        ax12.set_xlabel(f"Oscillator No.(N={N})", fontsize=12)
        ax11.set_ylabel("phase velocity\n" + r"($\log{|\dot{\theta}|}$)", fontsize=12)

        ax11.imshow(
            Temp_Ks[K], extent=[0, N, t_end, 0], aspect="auto", vmin=-8, vmax=3.4
        )
        ax12.imshow(
            Temp_Ksr[K], extent=[0, N, t_end, 0], aspect="auto", vmin=-8, vmax=3.4
        )
        # ax11.text(0,-5,f"m = {m}, K = {K}",fontsize=15)

        ax22.clear()
        ax22.plot(Temp_t, Temp_rs[K], label="Forward")
        ax22.plot(Temp_t, Temp_rsr[K], label="Backward")
        ax22.set_xlabel("Time[s]", fontsize=12)
        ax22.set_ylabel("Order\nparameter (r)", fontsize=12)
        ax22.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.20),
            fancybox=True,
            shadow=True,
            ncol=2,
        )
        ax22.set_ylim(0, 1)
        ax22.grid()
        fig.suptitle(f"m = {m}, K = {K}", fontsize=15)
        # fig.colorbar(im11, cax=cax11, orientation='vertical')
        # fig.colorbar(im12, cax=cax12, orientation='vertical')
        # ax2.text(0,-5,f"K = {K}",fontsize=15)
        fig.tight_layout()

    ani = FuncAnimation(fig, Update, frames=Ks, interval=500)
    return ani


def Make_to_animate(df, K_set, time_interval=10):
    """_summary_
    To make set when you make animation. df is to animate set,
    ex. K_set if you simulate one K, [[4.3, start time, end time]]
    ex. if you use more then 2 K set, [[4.3, 10, endtime],[4.5, 0, 50]]


    Args:
        df (Pandas Data frame): After you done `Hysteresis`, you can get Ksdf, Ksrdf. So put it to simulate
        K_set (2d array): Make 2d array, [[K1. start1, end1],[K2,start2,end2]]
        time_interval (int, optional): animation time is too slow you can adjust this value larger to make frame faseter. Defaults to 10.

    Returns:
        Check_K,To_animate: Check_K is To animate K,To animate is (K,timeidx) sets
    """
    To_animate = []
    K_set = np.array(K_set)
    Check_K = K_set[:, 0]
    t_ = df["ts"].iloc[0]

    def unzip_K_set(K_set):
        K_, t_start_time, t_end_time = K_set
        t_s = np.searchsorted(t_, t_start_time)
        t_e = np.searchsorted(t_, t_end_time)
        return K_, t_s, t_e

    for K_set_ in K_set:
        K_, t_s, t_e = unzip_K_set(K_set_)
        [
            To_animate.append((K_, t))
            for t in np.arange(t_s, t_e + 0.5, time_interval, dtype=int)
        ]
    return Check_K, To_animate


def Animate_phase(df, To_animate, Check_K, m):
    """_summary_
    To see phase vs phase velocity, phase velocity vs natural frequency, phase vs natural frequency.
    Use this animation you can check this system is really synchoronize
    Args:
        df (Pandas Data frame): After you done `Hysteresis`, you can get Ksdf, Ksrdf. So put it to simulate
        To_animate (_type_): After `Make_to_animate` excute you can get this value
        Check_K (_type_): After `Make_to_animate` excute you can get this value
        m (float): mass of oscillator
    Returns:
        ani: After waiting this result, you can see this animation with `HTML(ani.to_jshtml())` or `ani.save("some name.mp4")`
    """
    C_T = lambda theta: (theta + np.pi) % (2 * np.pi) - np.pi
    K_, time_idx = To_animate[0]
    N = df["theta_s"].iloc[0].shape[1]
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5));

    Target = df.loc[Check_K]
    T_ = Target["theta_s"].apply(C_T)
    O = Target["Omega"][K_]
    dTt_ = Target["dtheta_s"]
    Time = df["ts"].iloc[0]
    T, dTt, time = T_[K_][time_idx], dTt_[K_][time_idx], Time[time_idx]
    ax1.scatter(T, dTt, s=2, c=O, vmin=-5, vmax=5);
    ax1.set_ylim(-4, 4);
    ax1.set_xlim(-np.pi, np.pi);
    ax1.set_xlabel(r"phase ($\theta$)", fontsize=15);
    ax1.set_ylabel(r"phase verocity($\dot{\theta}$)", fontsize=15);

    ax2.scatter(T, O, c=O, s=2, vmin=-5, vmax=5);
    ax2.set_xlim(-np.pi, np.pi);
    ax2.set_ylim(-4, 4);
    ax2.set_xlabel(r"phase ($\theta$)", fontsize=15);
    ax2.set_ylabel(r"Natural frequency($\omega$)", fontsize=15);

    sca = ax3.scatter(dTt, O, c=O, s=2, vmin=-5, vmax=5);
    ax3.set_ylim(-4, 4);
    ax3.set_xlim(-4, 4);
    ax3.set_xlabel(r"phase verocity($\dot{\theta}$)", fontsize=15);
    ax3.set_ylabel(r"Natural frequency($\omega$)", fontsize=15);

    divider = make_axes_locatable(ax3);
    cax = divider.append_axes("right", size="5%", pad=0.05);
    cbar = fig.colorbar(sca, cax=cax, orientation="vertical", extend="both");
    cbar.set_label("Natural frequency($\omega$)", fontsize=15);
    fig.suptitle(f"N={N},m={m},K={K_},time={time}", fontsize=21);
    ax1.set_title(f"phase vs phase vel.", fontsize=18);
    ax2.set_title(f"phase vs Natural freq.", fontsize=18);
    ax3.set_title(f"phase vel. vs Natural freq.", fontsize=18);
    fig.tight_layout();

    def Animation_phase(K_time):
        K_, time_idx = K_time
        T = T_[K_][time_idx]
        dTt = dTt_[K_][time_idx]
        time = Time[time_idx]
        ax1.clear()
        ax1.scatter(T, dTt, s=2, c=O, vmin=-5, vmax=5)
        ax1.set_ylim(-4, 4)
        ax1.set_xlim(-np.pi, np.pi)
        ax1.set_xlabel(r"phase ($\theta$)", fontsize=15)
        ax1.set_ylabel(r"phase verocity($\dot{\theta}$)", fontsize=15)

        ax2.clear()
        ax2.scatter(T, O, c=O, s=2, vmin=-5, vmax=5)
        ax2.set_xlim(-np.pi, np.pi)
        ax2.set_ylim(-4, 4)
        ax2.set_xlabel(r"phase ($\theta$)", fontsize=15)
        ax2.set_ylabel(r"Natural frequency($\omega$)", fontsize=15)

        ax3.clear()
        sca = ax3.scatter(dTt, O, c=O, s=2, vmin=-5, vmax=5)
        ax3.set_ylim(-4, 4)
        ax3.set_xlim(-4, 4)
        ax3.set_xlabel(r"phase verocity($\dot{\theta}$)", fontsize=15)
        ax3.set_ylabel(r"Natural frequency($\omega$)", fontsize=15)
        # fig.colorbar(sca, ax = ax3)

        # divider = make_axes_locatable(ax3)
        # cax = divider.append_axes('right', size='5%', pad=0.05)
        # cbar =fig.colorbar(sca, cax=cax, orientation='vertical',extend="both")
        # cbar.set_label("Natural frequency($\omega$)",fontsize=15)
        fig.suptitle(f"N={N},m={m},K={K_},time={time:.02f}", fontsize=21)
        ax1.set_title(f"phase vs phase vel.", fontsize=18)
        ax2.set_title(f"phase vs Natural freq.", fontsize=18)
        ax3.set_title(f"phase vel. vs Natural freq.", fontsize=18)
        fig.tight_layout()

    ani = FuncAnimation(fig, Animation_phase, frames=To_animate, interval=50)
    return ani


def ddtheta_animation(df, To_animate, Check_K, m):
    int_ = np.linspace(0, 1, 100)
    color = plt.cm.viridis(int_)
    sorted_color = lambda x: color[np.searchsorted(int_, x)]

    K_, t_s = To_animate[0]
    ts_ = df["ts"].iloc[0]
    rs_ = df["rs"]
    color_ = rs_.apply(sorted_color)
    dt = ts_[1] - ts_[0]
    df = df.loc[Check_K]
    diff = lambda x: np.diff(x, axis=0) / dt
    df["ddtheta_s"] = df["dtheta_s"].apply(diff)
    df_ = df["ddtheta_s"]
    omega = df["Omega"][K_]
    max_ = df_.apply(np.max).max()
    min_ = df_.apply(np.min).min()

    print("max_,min_")
    print(max_, min_)
    N = df_.iloc[0].shape[1]

    fig = plt.figure(facecolor="white")
    ax = fig.subplots()
    ax.set_ylim(min_, max_)
    ax.set_xlabel("Oscillator No.", fontsize=13)
    ax.set_ylabel("phase acc.", fontsize=13)
    t_s_time = ts_[t_s]
    title = ax.set_title(
        r"$\ddot{\theta}(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}",
        fontsize=15,
        pad=30,
    )
    sca = ax.scatter(np.arange(N), (df_[K_][t_s]), c=omega, vmin=-4, vmax=4, s=3)
    KR = lambda df, K: df["rs"][K] * K
    KMR = lambda x, m: (4 / np.pi) * np.sqrt(x / m)
    O_lset = lambda x: np.searchsorted(omega, -x)
    O_rset = lambda x: np.searchsorted(omega, x)
    KR_ = KR(df, Check_K)
    KMR_ = KR_.apply(KMR, m=m)
    KR_lidx = KR_.apply(O_lset)
    KR_ridx = KR_.apply(O_rset)
    # KR_lidx = N - KR_ridx
    KMR_lidx = KMR_.apply(O_lset)
    KMR_ridx = KMR_.apply(O_rset)
    # KMR_lidx = N - KMR_ridx
    min_omega = Check_min_omega(m)
    
    KMR_lidx_max=KMR_lidx.apply(np.max)
    KMR_lidx_min=KMR_lidx.apply(np.min)
    KMR_ridx_max=KMR_ridx.apply(np.max)
    KMR_ridx_min=KMR_ridx.apply(np.min)
    
    KR_lidx_max=KR_lidx.apply(np.max)
    KR_lidx_min=KR_lidx.apply(np.min)
    KR_ridx_max=KR_ridx.apply(np.max)
    KR_ridx_min=KR_ridx.apply(np.min)
    
    (kr_l,) = plt.plot(
        [KR_lidx[K_][t_s], KR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:orange",
        label=r"$\Omega_{D}$(Depinning freq.)",
    )
    (kr_r,) = plt.plot(
        [KR_ridx[K_][t_s], KR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:orange"
    )
    (kr_rmax,) = plt.plot(
        [KR_ridx_max[K_], KR_ridx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmax,) = plt.plot(
        [KR_lidx_max[K_], KR_lidx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_rmin,) = plt.plot(
        [KR_ridx_min[K_], KR_ridx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmin,) = plt.plot(
        [KR_lidx_min[K_], KR_lidx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )

    (kmr_l,) = plt.plot(
        [KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:blue",
        label=r"$\Omega_{P}$(Pinning freq.)",
    )
    (kmr_r,) = plt.plot(
        [KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:blue"
    )
    (kmr_rmax,) = plt.plot(
        [KMR_ridx_max[K_], KMR_ridx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmax,) = plt.plot(
        [KMR_lidx_max[K_], KMR_lidx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_rmin,) = plt.plot(
        [KMR_ridx_min[K_], KMR_ridx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmin,) = plt.plot(
        [KMR_lidx_min[K_], KMR_lidx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )

    divider = make_axes_locatable(ax)
    rax = divider.append_axes("right", size="5%", pad=0.05)
    cax = divider.append_axes("right", size="5%", pad=0.35)
    cbar = fig.colorbar(sca, cax=cax, ax=cax, orientation="vertical", extend="both")
    cbar.set_label("Natural frequency($\omega$)", fontsize=12)
    # ax.legend(bbox_to_anchor=(0.0, -.03), loc="lower left",bbox_transform=fig.transFigure, ncol=2)
    ax.legend(
        bbox_to_anchor=(0.0, 1.01, 1, 0.1),
        loc="lower left",
        mode="expand",
        borderaxespad=0,
        ncol=3,
    )
    (rbar,) = rax.bar(0, rs_[K_][t_s])
    rax.set_ylim(0, 1)
    rax.set_title("r")
    rax.tick_params(
        labelleft=False,
        left=False,
        labelright=True,
        right=True,
        labelbottom=False,
        bottom=False,
    )
    fig.tight_layout()

    def Update(To_animate):
        K_, t_s = To_animate
        t_s_time = ts_[t_s]
        sca.set_offsets(np.c_[np.arange(N), (df_[K_][t_s])])
        rbar.set_height(rs_[K_][t_s])
        rbar.set_color(color_[K_][t_s])
        kr_l.set_xdata([KR_lidx[K_][t_s], KR_lidx[K_][t_s]])
        kr_r.set_xdata([KR_ridx[K_][t_s], KR_ridx[K_][t_s]])
        kmr_l.set_xdata([KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]])
        kmr_r.set_xdata([KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]])
        kmr_rmin.set_xdata([KMR_ridx_min[K_], KMR_ridx_min[K_]])
        kmr_rmax.set_xdata([KMR_ridx_max[K_], KMR_ridx_max[K_]])
        kmr_lmin.set_xdata([KMR_lidx_min[K_], KMR_lidx_min[K_]])
        kmr_lmax.set_xdata([KMR_lidx_max[K_], KMR_lidx_max[K_]])
        
        kr_rmin.set_xdata([KR_ridx_min[K_], KR_ridx_min[K_]])
        kr_rmax.set_xdata([KR_ridx_max[K_], KR_ridx_max[K_]])
        kr_lmin.set_xdata([KR_lidx_min[K_], KR_lidx_min[K_]])
        kr_lmax.set_xdata([KR_lidx_max[K_], KR_lidx_max[K_]])
        
        title.set_text(r"$\ddot{\theta}(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}")

    ani = FuncAnimation(fig, Update, frames=To_animate, interval=50)
    return ani


def dtheta_animation(df, To_animate, Check_K, m,max_divider = 100):
    int_ = np.linspace(0, 1, 100)
    color = plt.cm.viridis(int_)
    sorted_color = lambda x: color[np.searchsorted(int_, x)]

    K_, t_s = To_animate[0]
    ts_ = df["ts"].iloc[0]
    rs_ = df["rs"]
    color_ = rs_.apply(sorted_color)

    df = df.loc[Check_K]
    df_ = df["dtheta_s"]
    omega = df["Omega"][K_]
    max_ = df_.apply(np.max).max() / max_divider
    min_ = df_.apply(np.min).min() / max_divider

    N = df_.iloc[0].shape[1]
    print(f"max_/{max_divider},min_/{max_divider}")
    print(max_, min_)

    fig = plt.figure(facecolor="white")
    ax = fig.subplots()
    ax.set_ylim(min_, max_)
    ax.set_xlabel("Oscillator No.", fontsize=13)
    ax.set_ylabel("phase vel.", fontsize=13)
    t_s_time = ts_[t_s]
    # sca = ax.scatter(np.arange(1,N+1),(df_[t_s]),c=omega,vmin=-4,vmax=4,s=3)
    title = ax.set_title(
        r"$\dot{\theta}(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}", fontsize=15, pad=30
    )
    sca = ax.scatter(np.arange(0, N), (df_[K_][t_s]), c=omega, vmin=-4, vmax=4, s=3)
    divider = make_axes_locatable(ax)
    O_lset = lambda x: np.searchsorted(omega, -x)
    O_rset = lambda x: np.searchsorted(omega, x)
    KR = lambda df, K: df["rs"][K] * K
    KMR = lambda x, m: (4 / np.pi) * np.sqrt(x / m) # x = KR
    KR_ = KR(df, Check_K)
    KMR_ = KR_.apply(KMR, m=m)
    KR_lidx = KR_.apply(O_lset)
    KR_ridx = KR_.apply(O_rset)
    # KR_lidx = N - KR_ridx
    KMR_lidx = KMR_.apply(O_lset)
    KMR_ridx = KMR_.apply(O_rset)
    # KMR_lidx = N - KMR_ridx
    min_omega = Check_min_omega(m)
    
    KMR_lidx_max=KMR_lidx.apply(np.max)
    KMR_lidx_min=KMR_lidx.apply(np.min)
    KMR_ridx_max=KMR_ridx.apply(np.max)
    KMR_ridx_min=KMR_ridx.apply(np.min)
    
    KR_lidx_max=KR_lidx.apply(np.max)
    KR_lidx_min=KR_lidx.apply(np.min)
    KR_ridx_max=KR_ridx.apply(np.max)
    KR_ridx_min=KR_ridx.apply(np.min)
    
    (kr_l,) = plt.plot(
        [KR_lidx[K_][t_s], KR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:orange",
        label=r"$\Omega_{D}$(Depinning freq.)",
    )
    (kr_r,) = plt.plot(
        [KR_ridx[K_][t_s], KR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:orange"
    )
    (kr_rmax,) = plt.plot(
        [KR_ridx_max[K_], KR_ridx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmax,) = plt.plot(
        [KR_lidx_max[K_], KR_lidx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_rmin,) = plt.plot(
        [KR_ridx_min[K_], KR_ridx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmin,) = plt.plot(
        [KR_lidx_min[K_], KR_lidx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )

    (kmr_l,) = plt.plot(
        [KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:blue",
        label=r"$\Omega_{P}$(Pinning freq.)",
    )
    (kmr_r,) = plt.plot(
        [KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:blue"
    )
    (kmr_rmax,) = plt.plot(
        [KMR_ridx_max[K_], KMR_ridx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmax,) = plt.plot(
        [KMR_lidx_max[K_], KMR_lidx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_rmin,) = plt.plot(
        [KMR_ridx_min[K_], KMR_ridx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmin,) = plt.plot(
        [KMR_lidx_min[K_], KMR_lidx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )

    rax = divider.append_axes("right", size="5%", pad=0.1)
    cax = divider.append_axes("right", size="5%", pad=0.35)
    cbar = fig.colorbar(sca, cax=cax, ax=cax, orientation="vertical", extend="both")
    cbar.set_label("Natural frequency($\omega$)", fontsize=12)

    (rbar,) = rax.bar(0, rs_[K_][t_s], color=color_[K_][t_s])
    rax.set_ylim(0, 1)
    rax.set_title("r")
    rax.tick_params(
        labelleft=False,
        left=False,
        labelright=True,
        right=True,
        labelbottom=False,
        bottom=False,
    )
    fig.tight_layout()

    def Update(To_animate):
        K_, t_s = To_animate
        t_s_time = ts_[t_s]
        sca.set_offsets(np.c_[np.arange(1, N + 1), (df_[K_][t_s])])
        rbar.set_height(rs_[K_][t_s])
        rbar.set_color(color_[K_][t_s])
        kr_l.set_xdata([KR_lidx[K_][t_s], KR_lidx[K_][t_s]])
        kr_r.set_xdata([KR_ridx[K_][t_s], KR_ridx[K_][t_s]])
        kmr_l.set_xdata([KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]])
        kmr_r.set_xdata([KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]])
        kmr_rmin.set_xdata([KMR_ridx_min[K_], KMR_ridx_min[K_]])
        kmr_rmax.set_xdata([KMR_ridx_max[K_], KMR_ridx_max[K_]])
        kmr_lmin.set_xdata([KMR_lidx_min[K_], KMR_lidx_min[K_]])
        kmr_lmax.set_xdata([KMR_lidx_max[K_], KMR_lidx_max[K_]])
        title.set_text(r"$\dot{\theta}(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}")

    ani = FuncAnimation(fig, Update, frames=To_animate, interval=50)
    return ani


def theta_animation(df, To_animate, Check_K, m):
    int_ = np.linspace(0, 1, 100)
    color = plt.cm.viridis(int_)
    sorted_color = lambda x: color[np.searchsorted(int_, x)]
    sin = lambda x: np.sin(x)
    K_, t_s = To_animate[0]

    ts_ = df["ts"].iloc[0]
    rs_ = df["rs"]
    color_ = rs_.apply(sorted_color)
    df = df.loc[Check_K]
    df_ = df["theta_s"].apply(sin)
    N = df_.iloc[0].shape[1]
    omega = df["Omega"][K_]
    max_ = df_.apply(np.max).max()
    min_ = df_.apply(np.min).min()
    print("max,min")
    print(max_, min_)

    fig = plt.figure(facecolor="white")
    ax = fig.subplots()

    ax.set_ylim(min_, max_)
    ax.set_xlabel("Oscillator No.", fontsize=13)
    ax.set_ylabel(r"$sin(\theta)$", fontsize=13)
    t_s_time = ts_[t_s]
    title = ax.set_title(
        r"$\theta(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}", fontsize=15, pad=30
    )
    sca = ax.scatter(np.arange(1, N + 1), (df_[K_][t_s]), c=omega, vmin=-4, vmax=4, s=3)
    O_lset = lambda x: np.searchsorted(omega, -x)
    O_rset = lambda x: np.searchsorted(omega, x)
    KR = lambda df, K: df["rs"][K] * K
    KMR = lambda x, m: (4 / np.pi) * np.sqrt(x / m)
    KR_ = KR(df, Check_K)
    KMR_ = KR_.apply(KMR, m=m)
    KR_lidx = KR_.apply(O_lset)
    KR_ridx = KR_.apply(O_rset)
    # KR_lidx = N - KR_ridx
    KMR_lidx = KMR_.apply(O_lset)
    KMR_ridx = KMR_.apply(O_rset)
    # KMR_lidx = N - KMR_ridx
    min_omega = Check_min_omega(m)
    
    KMR_lidx_max=KMR_lidx.apply(np.max)
    KMR_lidx_min=KMR_lidx.apply(np.min)
    KMR_ridx_max=KMR_ridx.apply(np.max)
    KMR_ridx_min=KMR_ridx.apply(np.min)
    
    KR_lidx_max=KR_lidx.apply(np.max)
    KR_lidx_min=KR_lidx.apply(np.min)
    KR_ridx_max=KR_ridx.apply(np.max)
    KR_ridx_min=KR_ridx.apply(np.min)
    (kr_l,) = plt.plot(
        [KR_lidx[K_][t_s], KR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:orange",
        label=r"$\Omega_{D}$(Depinning freq.)",
    )
    (kr_r,) = plt.plot(
        [KR_ridx[K_][t_s], KR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:orange"
    )
    (kr_rmax,) = plt.plot(
        [KR_ridx_max[K_], KR_ridx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmax,) = plt.plot(
        [KR_lidx_max[K_], KR_lidx_max[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_rmin,) = plt.plot(
        [KR_ridx_min[K_], KR_ridx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )
    (kr_lmin,) = plt.plot(
        [KR_lidx_min[K_], KR_lidx_min[K_]], [min_, max_], ls='--', color="tab:orange",alpha=0.3
    )

    (kmr_l,) = plt.plot(
        [KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]],
        [min_, max_],
        ls="--",
        color="tab:blue",
        label=r"$\Omega_{P}$(Pinning freq.)",
    )
    (kmr_r,) = plt.plot(
        [KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]], [min_, max_], ls="--", color="tab:blue"
    )
    (kmr_rmax,) = plt.plot(
        [KMR_ridx_max[K_], KMR_ridx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmax,) = plt.plot(
        [KMR_lidx_max[K_], KMR_lidx_max[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_rmin,) = plt.plot(
        [KMR_ridx_min[K_], KMR_ridx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    (kmr_lmin,) = plt.plot(
        [KMR_lidx_min[K_], KMR_lidx_min[K_]], [min_, max_], ls='--', color="tab:blue",alpha=0.3
    )
    
    ax.legend(
        bbox_to_anchor=(0.0, 1.01, 1, 0.1),
        loc="lower left",
        mode="expand",
        borderaxespad=0,
        ncol=3,
    )

    divider = make_axes_locatable(ax)
    rax = divider.append_axes("right", size="5%", pad=0.1)
    cax = divider.append_axes("right", size="5%", pad=0.35)
    cbar = fig.colorbar(sca, cax=cax, ax=cax, orientation="vertical", extend="both")
    cbar.set_label("Natural frequency($\omega$)", fontsize=12)

    (rbar,) = rax.bar(0, rs_[K_][t_s], color=color_[K_][t_s])
    rax.set_ylim(0, 1)
    rax.set_title("r")
    rax.tick_params(
        labelleft=False,
        left=False,
        labelright=True,
        right=True,
        labelbottom=False,
        bottom=False,
    )
    fig.tight_layout()

    def Update(To_animate):
        K_, t_s = To_animate
        t_s_time = ts_[t_s]
        sca.set_offsets(np.c_[np.arange(1, N + 1), (df_[K_][t_s])])
        rbar.set_height(rs_[K_][t_s])
        rbar.set_color(color_[K_][t_s])
        kr_l.set_xdata([KR_lidx[K_][t_s], KR_lidx[K_][t_s]])
        kr_r.set_xdata([KR_ridx[K_][t_s], KR_ridx[K_][t_s]])
        kmr_l.set_xdata([KMR_lidx[K_][t_s], KMR_lidx[K_][t_s]])
        kmr_r.set_xdata([KMR_ridx[K_][t_s], KMR_ridx[K_][t_s]])
        kmr_rmin.set_xdata([KMR_ridx_min[K_], KMR_ridx_min[K_]])
        kmr_rmax.set_xdata([KMR_ridx_max[K_], KMR_ridx_max[K_]])
        kmr_lmin.set_xdata([KMR_lidx_min[K_], KMR_lidx_min[K_]])
        kmr_lmax.set_xdata([KMR_lidx_max[K_], KMR_lidx_max[K_]])
        
        kr_rmin.set_xdata([KR_ridx_min[K_], KR_ridx_min[K_]])
        kr_rmax.set_xdata([KR_ridx_max[K_], KR_ridx_max[K_]])
        kr_lmin.set_xdata([KR_lidx_min[K_], KR_lidx_min[K_]])
        kr_lmax.set_xdata([KR_lidx_max[K_], KR_lidx_max[K_]])
        
        title.set_text(r"$\theta(K,t)$" + f" m={m},K={K_},t={t_s_time:.02f}")

    ani = FuncAnimation(fig, Update, frames=To_animate, interval=50)
    return ani


def phase_cylindrical_animation(df, To_animate, Check_K, m):
    int_ = np.linspace(0, 1, 100)
    sin = lambda x: np.sin(x)
    cos = lambda x: np.cos(x)
    color = plt.cm.viridis(int_)
    sorted_color = lambda x: color[np.searchsorted(int_, x)]
    K_, t_s = To_animate[0]
    ts_ = df["ts"].iloc[0]
    rs_ = df["rs"]
    color_ = rs_.apply(sorted_color)
    df = df.loc[Check_K]
    df_sin = df["theta_s"].apply(sin)
    df_cos = df["theta_s"].apply(cos)
    N = df_sin.iloc[0].shape[1]
    omega = df["Omega"][K_]

    fig = plt.figure(facecolor="white")
    ax = fig.add_subplot(111, aspect="equal")
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    ax.set_ylabel(r"$sin(\theta)$", fontsize=13)
    ax.set_xlabel(r"$cos(\theta)$", fontsize=13)
    t_s_time = ts_[t_s]
    ax.set_title(r"$\theta(K,t)$" + f"m={m},K={K_},t={t_s_time:.02f}", fontsize=15)
    sca = ax.scatter(
        (df_cos[K_][t_s]), (df_sin[K_][t_s]), c=omega, vmin=-1, vmax=1, s=3
    )
    divider = make_axes_locatable(ax)
    rax = divider.append_axes("right", size="5%", pad=0.1)
    cax = divider.append_axes("right", size="5%", pad=0.35)
    cbar = fig.colorbar(sca, cax=cax, ax=cax, orientation="vertical", extend="both")
    cbar.set_label("Natural frequency($\omega$)", fontsize=12)

    (rbar,) = rax.bar(0, rs_[K_][t_s], color=color_[K_][t_s])
    rax.set_ylim(0, 1)
    rax.set_title("r")
    rax.tick_params(
        labelleft=False,
        left=False,
        labelright=True,
        right=True,
        labelbottom=False,
        bottom=False,
    )
    fig.tight_layout()

    def Update(To_animate):
        K_, t_s = To_animate
        t_s_time = ts_[t_s]
        sca.set_offsets(np.c_[(df_sin[K_][t_s]), (df_cos[K_][t_s])])
        rbar.set_height(rs_[K_][t_s])
        rbar.set_color(color_[K_][t_s])
        ax.set_title(r"$\theta(K,t)$" + f"m={m},K={K_},t={t_s_time:.02f}", fontsize=15)

    ani = FuncAnimation(fig, Update, frames=To_animate, interval=50)
    return ani
