import pandas as pd
import numpy as np
import difflib
import re
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image



#Load all data needed for recommendation
df_cb= pd.read_csv("cleaned_data/df_cb.csv")
popular_df= pd.read_csv("cleaned_data/popular_df.csv")
df_similarity=pd.read_csv("cleaned_data/df_similarity.csv")
df_title=pd.read_csv("cleaned_data/df_title.csv")
similar_df=pd.read_csv("cleaned_data/similar_df.csv", index_col=False)


#clean movie title
def regex_clean(title):
    clean = re.sub('[^a-z0-9A-Z ]','' ,title)
    clean= clean.lower() #set all alphabets to lower case
    return clean


# CONTENT-BASED FILTERING ALGORITHM
title_list= df_cb['clean_title'].tolist()
similar=similar_df.drop('Unnamed: 0', axis=1)

def norm_title_cb(title:str):
    title = regex_clean(title)
    close_match = difflib.get_close_matches(title ,title_list, n = 1)[0]
    return close_match

#Recommender system for content based Algorithm
def recommender_cb(title:str):
    title = regex_clean(title)
    close_match = difflib.get_close_matches(title ,title_list, n = 1)[0]
    idx= df_cb[df_cb['clean_title']== close_match].index
    lst=similar.loc[idx[0]]
    df_scores= pd.DataFrame({'score':lst, 'title': title_list})
    df_scores= df_scores.sort_values(by= 'score', ascending=False).reset_index(drop=True).drop(index=0)
    recommended =df_scores.head()
    recommend_movies= recommended['title']#.tolist()
    recommended_movies=df_cb[df_cb['clean_title'].isin(recommend_movies)]['title'].tolist()
    recommend_homepage=df_cb[df_cb['clean_title'].isin(recommend_movies)]['homepage'].tolist()
    recommended_poster=df_cb[df_cb['clean_title'].isin(recommend_movies)]['poster_path'].tolist()
    recommendation=pd.DataFrame({'movies':recommended_movies, 'homepage': recommend_homepage, 'poster_path': recommended_poster})
        
    return recommendation


#COLLABORATORY FILTERING ALGORITHM
def norm_title_cf(title:str):
    title = regex_clean(title)
    title = difflib.get_close_matches(title ,df_title['clean_title'], cutoff= 0.3, n = 1)[0]
    return title

#Recommender system for collaborative filtering Algorithm
df_similarity=df_similarity.set_index(['title'])
def recommender_cf(title:str):
    title = regex_clean(title)
    title = difflib.get_close_matches(title ,df_title['clean_title'], cutoff= 0.4, n = 1)[0]
    recommended_movies=df_similarity[title].sort_values(ascending=False).iloc[1:6]
    recommended=recommended_movies.index.tolist()
    recommended_movie=df_title[df_title['clean_title'].isin(recommended)]['title'].tolist()
    recommended_homepage=df_title[df_title['title'].isin(recommended_movie)]['homepage'].tolist()
    recommended_posterpath=df_title[df_title['title'].isin(recommended_movie)]['poster_path'].tolist()
    recommendation=pd.DataFrame({'movies':recommended_movie, 'homepage': recommended_homepage, 'poster_path': recommended_posterpath})
    
    return recommendation

#POPULARITY BASED ALGORITHM
def popular_recommender(popular_df):
    recommend_movies=popular_df.head(10)['title'].tolist()
    recommend_homepage=popular_df.head(10)['homepage'].tolist()
    recommend_poster=popular_df.head(10)['poster_path'].tolist()
    recommendation=pd.DataFrame({'movies':recommend_movies, 'homepage': recommend_homepage, 'poster_path': recommend_poster})

    return recommendation


def main():
    st.title('Movie Recommendation App')

    menu=["Home", "Recommend", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.text("Popular movies right now...")
        popular=popular_recommender(popular_df)
        for i in popular.iterrows():
            name=i[1][0]
            homepage=i[1][1]
            img_url=i[1][2]
            st.write('Title: ', name)
            st.write('url: ', homepage)     

    elif choice== "Recommend":
        st.subheader("Recommend Movies")
        search_title=st.text_input('Movie title')
        if st.button("Recommend"):
            if search_title is not None:
                st.text("Movie recommendations for: '{}'".format(norm_title_cb(search_title)))
                try:
                    result_cb=recommender_cb(search_title)
                    result_cf=recommender_cf(search_title)
                except:
                    st.text("Not found")
                
                for i in result_cb.iterrows():
                    name=i[1][0]
                    homepage=i[1][1]
                    img_url=i[1][2]
                    st.write('Title: ', name)
                    st.write('url: ', homepage)
                
                st.text("People that watched '{}' also watched:".format(norm_title_cf(search_title)))
                
                for i in result_cf.iterrows():
                    name=i[1][0]
                    homepage=i[1][1]
                    img_url=i[1][2]
                    st.write('Title: ', name)
                    st.write('url: ', homepage)
    else:
        st.subheader("About")
        st.text("Movie recommendation System, built with streamlit and python")
        st.text("Aided by other python libraries such as; pandas sklearn, difflib and more")
        st.text("See popular recommendations in homepage")
        st.text("Get content based recommedations under similar movies in 'Recommend' page")
        st.text("Get collaborative filtering recommedations under similar users in 'Recommend' page")

if __name__=='__main__':
    main()
