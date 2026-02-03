import streamlit as st
import pandas as pd
import os
from src.data_processor import load_csv, process_data
from src.analytics import calculate_metrics, get_best_worst_trades
from src.visualizer import (
    plot_equity_curve, 
    plot_win_loss_dist, 
    plot_pnl_dist, 
    plot_market_breakdown, 
    plot_rr_vs_pnl, 
    plot_monthly_pnl,
    save_fig_temp
)
from src.reporter import generate_pdf_report, cleanup_temp_images
from src.ui_components import manual_entry_ui, sidebar_credits

# Page Config
st.set_page_config(page_title="TradeTrack", layout="wide", initial_sidebar_state="expanded")

# Sidebar
sidebar_credits()

# Header
st.title("📊 TradeTrack - Trading Journal")
st.write("Track, analyze, and improve your trading performance.")

# Input Selection
tab1, tab2 = st.tabs(["📂 Upload CSV", "✍️ Manual Entry"])

with tab1:
    uploaded_file = st.file_uploader("Upload your trades CSV", type=["csv", "txt"])
    if uploaded_file:
        st.session_state.dataset = load_csv(uploaded_file)
        st.success("File uploaded successfully!")
    
    if not uploaded_file and 'dataset' not in st.session_state:
        st.info("⬆️ Upload a CSV to begin. Use the included `trade_log_template.csv` as a template.")

with tab2:
    manual_entry_ui()

if 'dataset' in st.session_state:
    df = st.session_state.dataset
    # Data Processing
    df, resolved = process_data(df)
    
    st.subheader("Preview of Data")
    st.dataframe(df.head(10), use_container_width=True)

    if st.button("📈 Get Full Analysis"):
        with st.spinner("Analyzing your trades..."):
            metrics = calculate_metrics(df, resolved)
            
            if metrics is None:
                st.error("Could not calculate metrics. Please ensure your data has a PnL column or enough info to calculate it (Entry, Exit, Quantity).")
            else:
                # 1. Metrics Display
                st.subheader("🔍 Key Performance Indicators")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Total Trades", f"{metrics['total_trades']}")
                k2.metric("Win Rate", f"{metrics['win_rate']:.2f}%")
                k3.metric("Avg Win", f"{metrics['avg_win']:.2f}")
                k4.metric("Avg Loss", f"{metrics['avg_loss']:.2f}")

                k5, k6, k7, k8 = st.columns(4)
                k5.metric("Expectancy", f"{metrics['expectancy']:.2f}")
                k6.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
                k7.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
                k8.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}")

                # 2. Charts
                st.subheader("📊 Performance Visualizations")
                temp_images = []

                # Row 1
                c1, c2 = st.columns(2)
                with c1:
                    fig1 = plot_equity_curve(metrics)
                    st.pyplot(fig1)
                    temp_images.append(save_fig_temp(fig1))
                with c2:
                    fig2 = plot_win_loss_dist(df, metrics["pnl_series"])
                    st.pyplot(fig2)
                    temp_images.append(save_fig_temp(fig2))

                # Row 2
                c3, c4 = st.columns(2)
                with c3:
                    fig3 = plot_pnl_dist(metrics["pnl_series"])
                    st.pyplot(fig3)
                    temp_images.append(save_fig_temp(fig3))
                with c4:
                    fig4 = plot_market_breakdown(df, resolved)
                    if fig4:
                        st.pyplot(fig4)
                        temp_images.append(save_fig_temp(fig4))
                    else:
                        st.info("Market data not available for breakdown.")

                # Row 3
                c5, c6 = st.columns(2)
                with c5:
                    fig5 = plot_rr_vs_pnl(df, resolved, metrics["pnl_series"])
                    if fig5:
                        st.pyplot(fig5)
                        temp_images.append(save_fig_temp(fig5))
                    else:
                        st.info("Risk:Reward data not available.")
                with c6:
                    fig6_plotly, fig6_mpl = plot_monthly_pnl(df, resolved, resolved["pnl"])
                    if fig6_plotly:
                        st.plotly_chart(fig6_plotly, use_container_width=True)
                        temp_images.append(save_fig_temp(fig6_mpl))
                    else:
                        st.info("Date data not available for monthly analysis.")

                # 3. Best/Worst Trades
                st.subheader("🏆 Best & Worst Trades")
                best, worst = get_best_worst_trades(df, resolved)
                
                cols_to_show = [resolved.get(k) for k in ["date", "market", "entry", "exit_price", "pnl"] if resolved.get(k) and resolved.get(k) in df.columns]
                
                t1, t2 = st.tabs(["Top 5 Wins", "Top 5 Losses"])
                with t1:
                    st.dataframe(best[cols_to_show] if cols_to_show else best, use_container_width=True)
                with t2:
                    st.dataframe(worst[cols_to_show] if cols_to_show else worst, use_container_width=True)

                # 4. Export
                st.subheader("📄 Export Report")
                pdf_buffer = generate_pdf_report(metrics, temp_images)
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name="trade_report.pdf",
                    mime="application/pdf"
                )
                
                # Cleanup
                cleanup_temp_images(temp_images)
                st.success("Analysis complete!")
