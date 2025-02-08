import streamlit as st
from streamlit.components.v1 import html


class CssStyle:
    button_style = """
	<style>	
	.stButton > button,.stDownloadButton > button{
			min-width: 80px;
			font-family: inherit;
			appearance: none;
			border: 2;
			border-radius: 5px;
			background: #F0FFFF;
			color: 000000;
			padding: 8px 16px;
			font-size: 1rem;
			cursor: pointer;
		}
	.stButton > button:hover {
	  background: #1d49aa;
	}
	.stDownloadButton > button:hover {
	  background: #1d49aa;
	}

	.stButton > button:focus {
	  outline: none;
	  box-shadow: 0 0 0 4px #cbd6ee;
	}
	.stDownloadButton > button:focus {
	  outline: none;
	  box-shadow: 0 0 0 4px #cbd6ee;
	}
	        </style>
	        """

    tabs_css = """
	<style>
	button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
			min-width: 70px;
			font-family: inherit;
			appearance: none;
			border: 2;
			border-radius: 16px;
			background: #7FFFD4;
			color: 0000FF;
			padding: 2px 10px;
			font-size: 1rem;
			cursor: pointer;
		}

	button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p:hover {
	  background: #1d49aa;
	}

	button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p:focus {
	  outline: none;
	  box-shadow: 0 0 0 4px #cbd6ee;
	}

	.shadowbox {
	  width: 15em;
	  border: 1px solid #333;
	  box-shadow: 8px 8px 5px #444;
	  padding: 8px 12px;
	  background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc);
	}
	</style>
	"""
    html_string = '''
	<script language="javascript">
	const text = 'test1';	
	const matches = Array.from(document.querySelectorAll('div')).filter(element =>
	  element.textContent.includes(text),
	);	
	console.log(matches); // 👉️ [div.box]	
	matches.forEach(match => {
	  console.log(match.textContent);
	  alert(match.textContent);
	  // 👉️ Bobby Hadz
	});	

	function showDiv(value) {
	document.getElementById('count').value = 500 * value;
	var first = getElementsByClassName('css-ocqkz7 e1tzin5v4');
	      if (first.style.display !== "none") {
        first.style.display = "none";
      } 
      else {
        first.style.display = "block";
      }

}
	</script>
	'''
    expander_css = '''
	    <style>
	        .streamlit-expanderHeader{
	        color: 000000;
			cursor: pointer;
			padding: 10px;
			background: #F0FFFF;
	        text-align:center;
	        font-weight: bold;

	    }
	    .streamlit-expanderHeader:hover,
		.streamlit-expanderHeader:focus {
		  background: #FAEBD7;
		  .streamlit-expanderHeader.content {
			background: #fff;
			overflow: hidden;
			height: 0;
			transition: 0.5s;
			box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.3);
			}

			.streamlit-expanderHeader> input[name="collapse"]:checked ~ .handle label:before {
		    transform: rotate(180deg);
		    transform-origin: center;
		    transition: 0.4s;
			    </style>

	'''
    menu_styles = {
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "red", "font-size": "16px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#1d49aa"},
        "nav-link-selected": {"background-color": "#1d49aa"},
    }
    table_style = """"
	<style>	
	.table {
	width: 100%;
	border: none;
	margin-bottom: 20px;
}
.table thead th {
	font-weight: bold;
	text-align: left;
	border: none;
	padding: 10px 15px;
	background: #d8d8d8;
	font-size: 14px;
	border-left: 1px solid #ddd;
	border-right: 1px solid #ddd;
}
.table tbody td {
	text-align: left;
	border-left: 1px solid #ddd;
	border-right: 1px solid #ddd;
	padding: 10px 15px;
	font-size: 14px;
	vertical-align: top;
}
.table thead tr th:first-child, .table tbody tr td:first-child {
	border-left: none;
}
.table thead tr th:last-child, .table tbody tr td:last-child {
	border-right: none;
}
.table tbody tr:nth-child(even){
	background: #f3f3f3;
}
</style>
	"""

    @classmethod
    def run(cls):
        html(cls.html_string)  # JavaScript works
        st.markdown(cls.tabs_css, unsafe_allow_html=True)
        st.markdown(cls.button_style, unsafe_allow_html=True)
        st.markdown(cls.expander_css, unsafe_allow_html=True)
