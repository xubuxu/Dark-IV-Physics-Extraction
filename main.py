import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from src.io_handler import DataLoader
from src.physics import DarkIVAnalyzer
from src.visualization import Visualizer
from src.reporting.excel_gen import generate_excel_report
from src.reporting.word_gen import WordReportBuilder
from src.reporting.ppt_gen import PPTReportBuilder
from src.config import DEFAULT_AREA

def main():
    # Configuration
    DATA_DIR = 'data'
    OUTPUT_DIR = 'output'
    TEMPLATE_DIR = 'templates'
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Initialize Reporters
    word_builder = WordReportBuilder(os.path.join(TEMPLATE_DIR, 'report_template.docx'))
    ppt_builder = PPTReportBuilder(os.path.join(TEMPLATE_DIR, 'slide_template.pptx'))
    
    ppt_builder.create_title_slide("Dark IV Analysis Report", "Automated Analysis")
    
    # Initialize Visualizer
    viz = Visualizer(style_dir='styles')
    
    results_list = []
    
    # Scan files
    files = []
    # Support multiple extensions
    for ext in ['*.csv', '*.txt', '*.xlsx', '*.iv']:
        files.extend(glob.glob(os.path.join(DATA_DIR, ext)))
        
    print(f"Found {len(files)} files in '{DATA_DIR}'.")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"Processing {filename}...")
        
        try:
            # 1. Load & Preprocess
            df = DataLoader.load_data(filepath)
            df = DataLoader.preprocess(df, area=DEFAULT_AREA)
            
            # 2. Physics Analysis
            analyzer = DarkIVAnalyzer(df)
            analyzer.smooth_data()
            analyzer.calculate_differential_resistance()  # Calculate Rdiff
            params = analyzer.extract_parameters()
            params['filename'] = filename
            results_list.append(params)
            
            # 3. Visualization - Generate all plots
            # Store plot streams for reports
            plot_streams_nature = {}
            plot_streams_business = {}
            
            # 3.1 Semi-log J-V Plot
            viz.set_style('nature')
            fig_nature, ax_nature = plt.subplots(figsize=(3.5, 2.625))
            viz.plot_semilog_jv(analyzer.df, ax_nature, title=f"{filename} - Dark J-V")
            plot_streams_nature['jv'] = viz.get_image_stream(fig_nature)
            plt.close(fig_nature)
            
            viz.set_style('business')
            fig_biz, ax_biz = plt.subplots(figsize=(8, 6))
            viz.plot_semilog_jv(analyzer.df, ax_biz, title=f"{filename} - Dark J-V")
            plot_streams_business['jv'] = viz.get_image_stream(fig_biz)
            plt.close(fig_biz)
            
            # 3.2 Ideality Factor Plot
            viz.set_style('nature')
            fig_n_nature, ax_n_nature = plt.subplots(figsize=(3.5, 2.625))
            viz.plot_ideality_factor(analyzer.df, ax_n_nature, title=f"{filename} - n(V)")
            plot_streams_nature['n'] = viz.get_image_stream(fig_n_nature)
            plt.close(fig_n_nature)
            
            viz.set_style('business')
            fig_n_biz, ax_n_biz = plt.subplots(figsize=(8, 6))
            viz.plot_ideality_factor(analyzer.df, ax_n_biz, title=f"{filename} - n(V)")
            plot_streams_business['n'] = viz.get_image_stream(fig_n_biz)
            plt.close(fig_n_biz)
            
            # 3.3 Differential Resistance Plot
            viz.set_style('nature')
            fig_r_nature, ax_r_nature = plt.subplots(figsize=(3.5, 2.625))
            viz.plot_differential_resistance(analyzer.df, ax_r_nature, title=f"{filename} - Rdiff(V)")
            plot_streams_nature['rdiff'] = viz.get_image_stream(fig_r_nature)
            plt.close(fig_r_nature)
            
            viz.set_style('business')
            fig_r_biz, ax_r_biz = plt.subplots(figsize=(8, 6))
            viz.plot_differential_resistance(analyzer.df, ax_r_biz, title=f"{filename} - Rdiff(V)")
            plot_streams_business['rdiff'] = viz.get_image_stream(fig_r_biz)
            plt.close(fig_r_biz)
            
            # 4. Add to Reports
            # Word: Add all three plots for each sample
            word_builder.add_sample_analysis(filename, params, plot_streams_nature)
            
            # PPT: Add all three plots as separate slides
            comments = f"J0: {params['J0']:.2e}\nn: {params['n']:.2f}\nRs: {params['Rs']:.1e}\nRsh: {params['Rsh']:.1e}"
            ppt_builder.create_chart_slide(f"Dark J-V: {filename}", plot_streams_business['jv'], comments)
            ppt_builder.create_chart_slide(f"Ideality Factor: {filename}", plot_streams_business['n'], 
                                          f"Ideality factor analysis\nExtracted n: {params['n']:.2f}")
            ppt_builder.create_chart_slide(f"Differential Resistance: {filename}", plot_streams_business['rdiff'], 
                                          f"Resistance analysis\nRsh: {params['Rsh']:.1e} Ω·cm²")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            
    # 5. Finalize Reports
    if results_list:
        df_results = pd.DataFrame(results_list)
        
        # Excel
        generate_excel_report(results_list, os.path.join(OUTPUT_DIR, 'summary.xlsx'))
        
        # Word Summary Table
        word_builder.add_summary_table(df_results)
        word_builder.save(os.path.join(OUTPUT_DIR, 'Dark_IV_Report.docx'))
        
        # PPT Summary Slide
        ppt_builder.create_summary_slide(df_results)
        ppt_builder.save(os.path.join(OUTPUT_DIR, 'Dark_IV_Presentation.pptx'))
        
        print(f"Analysis complete. Reports generated in '{os.path.abspath(OUTPUT_DIR)}'.")
    else:
        print("No valid results to report.")

if __name__ == "__main__":
    main()
